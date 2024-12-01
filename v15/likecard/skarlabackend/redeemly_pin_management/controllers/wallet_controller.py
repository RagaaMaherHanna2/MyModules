from odoo.http import route, content_disposition
import json
from odoo.http import request
from odoo.tools import config
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.exceptions import UserError, AccessDenied
from odoo import SUPERUSER_ID
import datetime
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
import requests
import uuid
from odoo.addons.redeemly_pin_management.services.notification_service import NotificationService

class RedeemlyWalletManagement(BaseController):
    @route("/exposed/wallet/get_service_provider_bank_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_service_provider_bank_list(self):
        if not request.env.user.is_merchant:
            raise UserError("Invalid Request")

        if request.env.user.is_sub_merchant:
            service_provider_id = request.env['merchant.package.invites'].with_user(SUPERUSER_ID). \
                search([('merchant', '=', request.env.user.parent_merchant.id)], limit=1, order='id desc').product.service_provider_id
            if not service_provider_id:
                service_provider_id = request.env['res.users'].sudo().search([('id', '=', request.env.user.parent_merchant.id),
                                                                              ('create_uid.is_service_provider', '=',
                                                                               True)]
                                                                             )
        else:
            service_provider_id = request.env['merchant.package.invites'].with_user(SUPERUSER_ID). \
                search([('merchant', '=', request.uid)], limit=1, order='id desc').product.service_provider_id
            if not service_provider_id:
                service_provider_id = request.env['res.users'].sudo().search([('id', '=', request.uid),
                                                                              ('create_uid.is_service_provider', '=',
                                                                               True)]
                                                                             ).create_uid
        banks = service_provider_id.bank_ids
        banks_res = []
        for bank in banks:
            val = {
                'id': bank.id,
                'bank_name': bank.bank_id.name,
                'bic': bank.bank_id.bic,
                'acc_number': bank.acc_number,
                'account_type': bank.account_type,
                'account_class': bank.account_class,
                'iban': bank.iban,
                'adib_swift_code': bank.adib_swift_code,
            }
            banks_res.append(val)
        return BaseController._create_response(banks_res)

    @route("/exposed/wallet/get_merchant_bank_transfer_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_merchant_bank_transfer_list(self):
        if request.env.user.is_service_provider:
            raise UserError("Access Denied")
        if request.env.user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["6"], user=request.env.user)
        query_options = json.loads(request.httprequest.data)['params']
        filter = query_options.get('filter')
        offset = query_options.get('offset') if query_options.get('offset') else 0
        limit = query_options.get('limit') if query_options.get('limit') else 20
        type = query_options.get('type')
        id = query_options.get('id')
        if request.env.user.is_sub_merchant:
            domain = [('partner_id', '=', request.env.user.parent_merchant.partner_id.id)]
        else:
            domain = [('partner_id', '=', request.jwt_partner_id)]
        if type:
            domain += [('type', '=', type)]

        if filter == 'invoice_payment':
            raise UserError("Access Denied")

        if filter:
            domain += [('state', '=', filter)]
        if id:
            domain += [('id', '=', id)]
        items = request.env['pin.management.bank.transfer.request'].with_user(1).search(domain, limit=limit or 20,
                                                                                  offset=offset or 0,
                                                                                  order='create_date desc')
        items_count = request.env['pin.management.bank.transfer.request'].with_user(1).search_count(domain)
        data = [item.serialize_for_api() for item in items]
        res = {'data': data, 'totalCount': items_count}
        return BaseController._create_response(res)

    @route("/exposed/wallet/get_fees_invoice_payments",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_fees_invoice_payments(self):
        if not request.env.user.is_service_provider:
            raise UserError("Access Denied")
        query_options = json.loads(request.httprequest.data)['params']
        filter = query_options.get('filter')
        offset = query_options.get('offset') if query_options.get('offset') else 0
        limit = query_options.get('limit') if query_options.get('limit') else 20
        id = query_options.get('invoice_id')
        domain = [('partner_id', '=', request.jwt_partner_id), ('type', '=', 'invoice_payment')]
        if filter:
            domain += [('state', '=', filter)]
        if id:
            domain += [('invoice_id', '=', id)]
        items = request.env['pin.management.bank.transfer.request'].with_user(1).search(domain, limit=limit or 20,
                                                                                        offset=offset or 0,
                                                                                        order='create_date desc')
        items_count = request.env['pin.management.bank.transfer.request'].with_user(1).search_count(domain)
        data = [item.serialize_for_api() for item in items]
        res = {'data': data, 'totalCount': items_count}
        return BaseController._create_response(res)

    @route("/exposed/wallet/create_bank_transfer_request",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def create_bank_transfer_request(self):
        item = json.loads(request.httprequest.data)['params']
        if request.env.user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["6"], user=request.env.user)
        if request.env.user.is_merchant or \
                (item.get('type') == 'invoice_payment' and request.env.user.is_service_provider):
            if item.get('type') == 'invoice_payment':
                # check to bank are from company valid bank
                company_banks = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1).partner_id.bank_ids
                if not item.get('toBank') in company_banks.ids:
                    raise UserError("Invalid skarla bank")
                # check payment total value  == invoice amount total
                invoice = request.env['account.move'].sudo().search([('id', '=', item.get('invoice_id')),
                                                                     ('partner_id', '=', request.env.user.partner_id.id),
                                                                     ('payment_state', '!=', 'paid')
                                                                     ])
                if not invoice:
                    raise UserError("Invalid invoice")
                if invoice.amount_total != item.get('transferAmount'):
                    raise UserError("Transferred amount should be equal to invoice amount total")

                count = request.env['pin.management.bank.transfer.request'].sudo().\
                    search_count([('invoice_id', '=', item.get('invoice_id')),
                                  ('state', '!=', 'rejected')])
                if count > 0:
                    raise UserError("Payment Request Already Created Please Check Details")
            if request.env.user.is_sub_merchant:
                partner_id = request.env.user.parent_merchant.partner_id.id
            else:
                partner_id = request.env.user.partner_id.id
            val = {
                'bank': item.get('bank'),
                'toBank': item.get('toBank'),
                'transferAmount': item.get('transferAmount'),
                'state': 'draft',
                'note': '',
                'type': item.get('type'),
                'bankTransferImage': item.get('bankTransferImage')['file'] if item.get('bankTransferImage') else False,
                'partner_id': partner_id,
                "invoice_id": item.get('invoice_id') if item.get('type') == 'invoice_payment' else False
            }
            item = request.env['pin.management.bank.transfer.request'].sudo().with_context(tracking_disable=True).create(val)

            NotificationService.Send_Notification_email(user=request.env.user , self = item)

            return BaseController._create_response(data=item.serialize_for_api())
        else:
            return BaseController._create_response('Only Available For Merchants')

    @route("/exposed/wallet/approve_reject_bank_transfer_request",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def approve_reject_bank_transfer_request(self, **kw):
        if request.env.user.is_service_provider:
            validated = BaseController.get_validated(kw, {
                "id": "number|required",
                "state": "string|required",
                "note": "string"
            })
            bank_transfer = request.env['pin.management.bank.transfer.request'].\
                with_user(SUPERUSER_ID).\
                search([('id', '=', validated['id'])])
            if not bank_transfer:
                raise UserError("Invalid Request")
            count = request.env['merchant.package.invites'].\
                with_user(SUPERUSER_ID).search_count([('merchant', '=', bank_transfer.partner_id.user_ids.id),
                                                      ('product.service_provider_id', '=', request.env.user.id)
                                                     ])
            if count == 0:
                raise UserError(f"Invalid Request Please Insure That {bank_transfer.partner_id.name} "
                                f"has invited to a product")

            if validated['state'] == 'approved' and bank_transfer.state == 'draft':
                bank_transfer.action_approve()
                bank_transfer.note = validated['note']
                NotificationService.Send_Notification_email(user=request.env.user, self=bank_transfer)

            if validated['state'] == 'rejected' and bank_transfer.state == 'draft':
                bank_transfer.action_reject()
                bank_transfer.note = validated['note']
                NotificationService.Send_Notification_email(user=request.env.user, self=bank_transfer)
            return BaseController._create_response('ok')
        else:
            return BaseController._create_response('Invalid Request')

    @route("/exposed/wallet/get_company_bank_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_company_bank_list(self, **kw):
        if request.env.user.is_service_provider:
            company_banks = request.env['res.company'].sudo().search([('id', '=', 1)], limit=1).partner_id.bank_ids
            data = [{
                "id": item.id,
                "bank_name": item.bank_id.name,
                "bic": item.bank_id.bic,
                "acc_number": item.acc_number,
                "account_type": item.account_type,
                "account_class": item.account_class,
                "iban": item.iban,
                "adib_swift_code": item.adib_swift_code
            } for item in company_banks]

            return BaseController._create_response(data=data)
        else:
            return BaseController._create_response('Invalid Request')

    @route("/exposed/wallet/get_invoice_payments",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_invoice_payments(self, **kw):
        validated = BaseController.get_validated(kw, {
            "id": "number",
            "limit": "number",
            "offset": "number"
        })
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        id = validated.get('id')
        if request.env.user.is_service_provider:
            domain = [('type', '=', 'invoice_payment'),
                      ('create_uid', '=', request.uid)
                      ]
            if id:
                domain.append(('id', '=', id))
            items = request.env['pin.management.bank.transfer.request'].sudo().search(domain, limit=limit or 20,
                                                                                            offset=offset or 0,
                                                                                            order='create_date desc')
            items_count = request.env['pin.management.bank.transfer.request'].sudo().search_count(domain)
            data = []
            for item in items:
                val = item.serialize_for_api()
                data.append(val)
            res = {'data': data, 'totalCount': items_count}
            return BaseController._create_response(data=res)
        else:
            return BaseController._create_response('Invalid Request')

    @route("/exposed/wallet/get_sp_charge_request",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_sp_charge_request(self, **kw):
        if request.env.user.is_service_provider:
            validated = BaseController.get_validated(kw, {
                "merchant_name": "string",
                "merchant_id": "number",
                "merchant_reference": "string",
                "date": "string",
                "filter": "string",
                "offset": "number",
                "limit": "number",
                "id": "number"
            })
            limit = validated.get('limit') if validated.get('limit') else 20
            offset = validated.get('offset') if validated.get('offset') else 0
            domain = [('toBank.partner_id.user_ids.id', '=', request.uid)]
            if validated.get('merchant_name'):
                domain.append(('partner_id.name', 'ilike', validated['merchant_name']))
            if validated.get('merchant_id'):
                domain.append(('partner_id.user_ids.id', '=', validated['merchant_id']))
            if validated.get('merchant_reference'):
                domain.append(('partner_id.user_ids.reference', '=', validated['merchant_id']))
            if validated.get('id'):
                domain.append(('id', '=', validated['id']))
            if validated.get('date'):
                domain.append('create_date', '>=', validated['date'])
            if validated.get('filter'):
                domain.append(('state', '=', validated.get('filter')))

            bank_transfers = request.env['pin.management.bank.transfer.request']. \
                with_user(SUPERUSER_ID). \
                search(domain, limit=limit, offset=offset, order='create_date desc')
            items_count = request.env['pin.management.bank.transfer.request']. \
                with_user(SUPERUSER_ID). \
                search_count(domain)
            data = []
            for item in bank_transfers:
                val = item.serialize_for_api()
                data.append(val)
            res = {'data': data, 'totalCount': items_count}
            return BaseController._create_response(res)
        else:
            return BaseController._create_response('Invalid Request')

    @route("/exposed/wallet/get_user_balance",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_user_wallet_balance(self):
        user_id = request.env['res.users'].with_user(SUPERUSER_ID).sudo().search([('id', '=', request.uid)])
        if user_id.is_sub_merchant:
            balance = self.get_user_balance(user_id.parent_merchant)
            res = {'balance': round(balance, 2),
                   'currency': self.get_user_currency_symbol(user_id.parent_merchant)}
        else:
            balance = self.get_user_balance(user_id)
            res = {'balance': round(balance, 2),
                   'currency': self.get_user_currency_symbol(user_id)}
        return BaseController._create_response(res)

    @route("/exposed/wallet/get_wallet_balance_online",
           type="json",
           auth="none",
           save_session=False,
           cors=config.get('control_panel_url'))
    def get_wallet_balance_online(self, **kw):
        user_id = BaseController.key_authenticate(kw)
        balance = self.get_user_balance(user_id)
        res = {'balance': round(balance, 2),
               'currency': self.get_user_currency_symbol(user_id)}
        return BaseController._create_response(res)

    @staticmethod
    def get_user_balance(user_id):
        partner_id = user_id.partner_id
        return partner_id.sudo().balance

    @staticmethod
    def get_user_currency_symbol(user_id):
        return user_id.sp_currency.symbol

    @route("/exposed/wallet/get_balance_report_data",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_balance_report_data(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider and not user.is_merchant:
            raise AccessDenied()

        packages = [{'name': item.package_name, 'id': item.id, 'reference': item.name}
                    for item in request.env['package'].with_user(1).search([('service_provider_id', '=', user.id)])]
        products = [{'id': item.id, "name": item.name}
                    for item in request.env['package.generation.request.line'].with_user(1).\
            search([('generation_request.package.service_provider_id', '=', user.id)]).product]
        merchants = [{'id': item.id, "name": item.name, "reference": item.reference}
                     for item in request.env['package.codes'].with_user(1).\
                    search([('create_uid', '=', user.id)]).pulled_by]
        res = {
            "packages": packages,
            "products": products,
            "merchants": merchants
        }
        return BaseController._create_response(res)

    @route("/exposed/wallet/get_balance_report",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_balance_report(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider and not user.is_merchant:
            raise AccessDenied()

        validated = BaseController.get_validated(kw, {
            "packages": "list",
            "merchants": "list",
            "products": "list",
            "limit": "number",
            "offset": "number"
        })
        limit = validated['limit']
        offset = validated['offset']
        domain = [('partner_id', '=', user.partner_id.id),
                  ('account_id', '=', request.env.ref('redeemly_pin_management.account_wallet_debit').id)
                  ]
        if validated['packages']:
            domain.append(('move_id.invite_id.package', 'in', validated['packages']))
        if validated['merchants']:
            domain.append(('move_id.invite_id.merchant', 'in', validated['merchants']))
        if validated['products']:
            domain.append(('move_id.package_product_id', 'in', validated['products']))
        items = request.env['account.move.line'].sudo().search(domain, limit=limit, offset=offset, order='date desc')
        res = [
            {
                "date": datetime.datetime.strftime(item.date,
                                                        DATETIME_FORMAT),
                "balance": item.balance,
                "ref": item.move_id.name,
                "product": item.move_id.package_product_id.name if item.move_id.package_product_id else '',
                "merchant": item.move_id.invite_id.merchant.name if item.move_id.invite_id.merchant else '',
                "package_name": item.move_id.invite_id.package.package_name if item.move_id.invite_id.package else '',
                "package_name_ar": item.move_id.invite_id.package.package_name_ar if item.move_id.invite_id.package else '',
                "description": item.name

            }
            for item in items
        ]
        items_count = request.env['account.move.line'].with_user(1).search_count(domain)
        return BaseController._create_response({'data': res, 'totalCount': items_count})

    @route("/exposed/wallet/create_bank_information",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_bank_information(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider and not user.is_merchant:
            raise AccessDenied()
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["6"], user=user)

        validated_input = BaseController.get_validated(kw, {
            "bank_name": "string|required",
            "bic": "string|required",
            "acc_number": "string|required",
            "account_type": "string|required",
            "account_class": "string|required",
            "iban": "string|required",
            "adib_swift_code": "string|required"
        })
        if not validated_input.get('bank_name') \
            or not validated_input.get("bic") \
            or not validated_input.get("acc_number") \
            or not validated_input.get("account_type") \
            or not validated_input.get("account_class") \
            or not validated_input.get("adib_swift_code") \
            or not validated_input.get("iban") :
            raise UserError ("Missing Value")
        bank = request.env['res.bank'].sudo().create({
            'name': validated_input['bank_name'],
            'bic': validated_input['bic']
        })

        if user.is_sub_merchant:
            partner_id = user.parent_merchant.partner_id.id
        else:
            partner_id = user.partner_id.id

        bank_details = request.env['res.partner.bank'].sudo().create({
            'bank_id': bank.id,
            'acc_number': validated_input['acc_number'],
            'account_type': validated_input['account_type'],
            'account_class': validated_input['account_class'],
            'iban': validated_input['iban'],
            'adib_swift_code': validated_input['adib_swift_code'],
            'partner_id': partner_id
        })
        res = {
            'id': bank_details.id,
            'bank_name': bank_details.bank_id.name,
            'bic': bank_details.bank_id.bic,
            'acc_number': bank_details.acc_number,
            'account_class': bank_details.account_class,
            'account_type': bank_details.account_type,
            'iban': bank_details.iban,
            'adib_swift_code': bank_details.adib_swift_code,
        }
        return BaseController._create_response(res)

    @route("/exposed/wallet/edit_bank_information",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def edit_bank_information(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider and not user.is_merchant:
            raise AccessDenied()

        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["6"], user=user)

        validated_input = BaseController.get_validated(kw, {
            "id": "required|number",
            "bank_name": "required|string",
            "bic": "required|string",
            "acc_number": "required|string",
            "account_type": "required|string",
            "account_class": "required|string",
            "iban": "required|string",
            "adib_swift_code": "required|string"
        })
        if not validated_input.get('bank_name') \
            or not validated_input.get("bic") \
            or not validated_input.get("acc_number") \
            or not validated_input.get("account_type") \
            or not validated_input.get("account_class") \
            or not validated_input.get("adib_swift_code") \
            or not validated_input.get("iban") :
            raise UserError ("Missing Value")
        bank = request.env['res.partner.bank'].sudo().search([('id', '=', validated_input['id'])])
        if user.is_sub_merchant:
            if not bank or bank.partner_id.id != user.parent_merchant.partner_id.id:
                raise UserError("Bank Not Found")
        else:
            if not bank or bank.partner_id.id != user.partner_id.id:
                raise UserError("Bank Not Found")
        bank.bank_id.name = validated_input['bank_name']
        bank.bank_id.bic = validated_input['bic']
        bank.acc_number = validated_input['acc_number']
        bank.account_type = validated_input['account_type']
        bank.account_class = validated_input['account_class']
        bank.iban = validated_input['iban']
        bank.adib_swift_code = validated_input['adib_swift_code']
        res = {
            'id': bank.id,
            'bank_name': bank.bank_id.name,
            'bic': bank.bank_id.bic,
            'acc_number': bank.acc_number,
            'account_type': bank.account_type,
            'account_class': bank.account_class,
            'iban': bank.iban,
            'adib_swift_code': bank.adib_swift_code,
        }
        return BaseController._create_response(res)

    @route("/exposed/wallet/get_banks_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_banks_list(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider and not user.is_merchant:
            raise AccessDenied()

        validated = BaseController.get_validated(kw, {
            "bank_name_filter": "string"
        })
        bank_name_filter = validated.get('bank_name_filter')
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["6"], user=user)
            domain = [('partner_id', '=', user.parent_merchant.partner_id.id)]
        else:
            domain = [('partner_id', '=', user.partner_id.id)]
        if bank_name_filter:
            domain.append(('bank_id.name', 'ilike', bank_name_filter))
        banks = request.env['res.partner.bank'].sudo().search(domain)
        res = [{
            'id': bank.id,
            'bank_name': bank.bank_id.name,
            'bic': bank.bank_id.bic,
            'acc_number': bank.acc_number,
            'account_type': bank.account_type,
            'account_class': bank.account_class,
            'iban': bank.iban,
            'adib_swift_code': bank.adib_swift_code,
        } for bank in banks]

        return BaseController._create_response(res)

    @route("/exposed/wallet/get_fees_invoices",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_fees_invoices(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()

        validated = BaseController.get_validated(kw,
            { "offset": "int", "limit": "int", "type": "string", "id": "number"},
        )
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get('limit') else 20
        type = validated.get("type")
        id = validated.get("id")
        domain = [('partner_id', '=', user.partner_id.id), ('move_type', '=','out_invoice'),
                  ('state', 'in', ['draft', 'posted'])]
        if type:
            domain.append(('invoice_line_ids.name', 'ilike', type))
        if id:
            domain.append(('id', '=', id))
        invoices = request.env['account.move'].sudo().search(domain, limit=limit, offset=offset, order='create_date desc')
        res = [item.serialize_for_api() for item in invoices]
        count = request.env['account.move'].sudo().search_count(domain)
        return BaseController._create_response(data={'data': res, 'totalCount': count})

    @route(
        "/exposed/download_bank_transfer_image",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_bank_transfer_image(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'bankTransferImage'),
                  ('res_model', '=', 'pin.management.bank.transfer.request')
                  ]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain, limit=1)
        bank_request = request.env['pin.management.bank.transfer.request'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        if not bank_request:
            raise UserError("Not Found")
        file = requests.get(attach.url, timeout=5)
        if file:
            content = file.content
            filename = 'Bank Request - %s.%s' % (bank_request.sequence, file.headers['content-type'].split('/')[1])
            pdfhttpheaders = [('Content-Type', attach.mimetype), ('Content-Length', len(content)),
                              ('Content-Disposition', content_disposition(filename))
                              ]
            return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()

    @route(
        "/exposed/download_report_pdf",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_daily_report_pdf(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'report'),
                  ('res_model', '=', 'daily.income.report')
                  ]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain, limit=1)
        rep = request.env['daily.income.report'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        if not rep:
            raise UserError("Not Found")
        file = requests.get(attach.url, timeout=5)
        if file:
            content = file.content
            filename = 'Daily-income-report of date %s.%s' % (rep.from_date.strftime('%Y-%m-%d'), 'pdf')
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content)),
                              ('Content-Disposition', content_disposition(filename))
                              ]
            return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()

    @route(
        "/exposed/wallet/initialize_balance",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors='*',
        csrf=False
    )
    def initialize_balance(self, **kw):
        # ==========correct auto generated true for prepaid
        # products = request.env['product.template'].with_user(SUPERUSER_ID).search([('is_prepaid', '=', True)])
        # for product in products:
        #     product.serials_auto_generated = True
        # partner = request.env['res.partner'].with_user(SUPERUSER_ID).search([], limit=1)
        # partner.compute_balance_after_change()
        # =============================================
        # users = request.env['res.users'].with_user(SUPERUSER_ID).search([('is_service_provider', '=', True)])
        # for user in users:
        #     if not user.sp_hash:
        #         user.sp_hash = uuid.uuid4()
        # =============================================
        # sql = """
        #                 DELETE FROM ir_model_fields WHERE model = 'product.attribute.definition';
        #                 DELETE FROM ir_model_constraint WHERE model = (SELECT id FROM ir_model WHERE model = 'product.attribute.definition');
        #                 DELETE FROM ir_model_relation WHERE model = (SELECT id FROM ir_model WHERE model = 'product.attribute.definition');
        #                 DELETE FROM ir_model WHERE model = 'product.attribute.definition';
        #
        #                """
        # request.env.cr.execute(sql)
        return request.redirect('/web?#')
    @route("/exposed/wallet/get_all_merchants_balance",
           type="json",
           auth="none",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False
           )
    def get_all_merchants_balance(self, **kw):
        key = request.httprequest.headers.get('Authorization')
        if not key or key != '0F47583BFFC356F559C8D3BAF7C5B4AAFE00F79AF82EFF5433FC50058FADBE27':
            raise AccessDenied()
        try:
            merchant_users = request.env['res.users'].sudo().search([('is_merchant', '=', True)])
            if not merchant_users:
                return BaseController._create_response([],"ok",'No merchant users found.')
            else:
                data = []
                for merchant in merchant_users:
                    data.append({
                        'name': merchant.name,
                        "email": merchant.login,
                        'balance': merchant.partner_id.balance,
                        'currency': merchant.sp_currency.name,
                    })

                res = {'data': data, 'totalCount': len(merchant_users)}
        except Exception as e:
            return BaseController._create_response({}, 400, str(e))
        return BaseController._create_response(res)
