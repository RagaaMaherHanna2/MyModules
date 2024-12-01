import logging
from datetime import datetime, timedelta
import requests
from odoo.http import content_disposition
from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT, DATE_FORMAT
from odoo.http import request
import jwt
import time
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied


class PullController(BaseController):
    @http.route(
        "/exposed/pull_codes",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def pull_codes_online(self, **kw):
        user = BaseController.key_authenticate(kw)
        if not user or not user.is_merchant:
            raise AccessDenied()
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["1.2"], user=user)
            pulled_codes = PullController.pull_codes(kw, user.parent_merchant)
        else:
            pulled_codes = PullController.pull_codes(kw, user)
        return BaseController._create_response(pulled_codes)

    @http.route(
        "/exposed/pull_codes_offline",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def pull_codes_offline(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user or not user.is_merchant:
            raise AccessDenied()
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["1.2"], user=user)
            pulled_codes = PullController.pull_codes(kw, user.parent_merchant)
        else:
            pulled_codes = PullController.pull_codes(kw, user)
        # pulled_codes = PullController.pull_codes(kw, user)
        return BaseController._create_response(pulled_codes)

    @staticmethod
    def pull_codes(kw, user):

        validated = BaseController.get_validated(kw, {
            "product": "number|required",
            "quantity": "number",
            "user_id": "string",
            "email_id": "string",
            "customer_mobile_number": "string",
            "mobile_country_code": "string",
            "business_reference": "string",
            "customer_name": "string",
            "distributor": "string",
            "country_of_generation_parameters": "string"
        })

        now = datetime.now()
        quantity = validated["quantity"]
        email_id = validated["email_id"]
        customer_mobile_number = validated["customer_mobile_number"] if validated["customer_mobile_number"] else False
        mobile_country_code = validated["mobile_country_code"] if validated["mobile_country_code"] else False
        business_reference = validated["business_reference"] if validated["business_reference"] else False
        distributor = validated["distributor"] if validated["distributor"] else False
        country_of_generation_parameters = validated["country_of_generation_parameters"] if validated[
            "country_of_generation_parameters"] else False
        if not quantity:
            quantity = validated["quantity"] = 1
        if quantity <= 0 or quantity >= 50000:
            raise UserError("Invalid Quantity")

        invite = request.env['merchant.package.invites'].with_user(1).search([
            ("product.id", '=', validated['product']),
            ('merchant', '=', user.id),
            ('enabled', '=', True),
        ])

        if not invite:
            raise UserError("Product Not Found")

        # if invite.expiry_date and invite.expiry_date < datetime.today():
        #     raise UserError("Invitation Expired")
        if invite.product.is_prepaid and not email_id:
            raise UserError("Email ID Required")
        if not invite.unlimited and invite.pulled_serials_count + quantity > invite.limit:
            raise UserError(f"Pull Limit Exceeded , Remaining {invite.limit - invite.pulled_serials_count}")

        if not invite.product.serials_auto_generated and not invite.product.is_prepaid:
            if quantity > invite.product.product_actual_stock:
                raise UserError("Not Enough Quantity")
        if invite.product.is_prepaid and not email_id:
            raise UserError("You Must enter email id Please")

        deducted_balance = invite.price * quantity

        if invite.tax_id:
            if invite.tax_id.amount_type == 'percent':
                deducted_balance = deducted_balance + (deducted_balance * invite.tax_id.amount / 100)
            else:
                deducted_balance = deducted_balance + invite.tax_id.amount

        product = invite.product.sudo()
        lines_vals = [
            (0, 0, {
                'name': 'test',
                'product_id': product.product_variant_ids[0].id,
                'price_unit': invite.price,
                'product_uom_qty': quantity,
                'tax_id': [invite.tax_id.id] if invite.tax_id else None,
                'merchant_tax': invite.tax_id.amount if invite.tax_id else 0

            })]
        order = request.env['sale.order'].sudo().create({
            'state': 'draft',
            'partner_id': user.partner_id.id,
            'service_provider_id': invite.product.service_provider_id.id,
            'order_line': lines_vals,
            'date_order': now
        })
        serials = product.pull_serials(merchant=user, order_id=order, customer_mobile_number=customer_mobile_number,
                                       mobile_country_code=mobile_country_code, business_reference=business_reference,
                                       quantity=quantity, email_id=email_id, now=now, distributor=distributor,
                                       country_of_generation_parameters=country_of_generation_parameters)

        if len(serials) != quantity:
            raise UserError("Not Enough Quantity, some serials are expired")
        res = {}

        order.action_confirm()
        pulled_serials = []
        product_quantity_group_by = {}
        aes_cipher = request.env['aes.cipher'].create([])
        for serial in serials:
            serial_code = aes_cipher.decrypt(serial[1])
            parts = [serial_code[i:i + 4] for i in range(0, len(serial_code), 4)]

            # Join the parts with a "-"
            result = "".join(parts)
            if serial[2] not in product_quantity_group_by.keys():
                product_quantity_group_by[serial[2]] = {'name': serial[3], 'quantity': 0}
            product_quantity_group_by[serial[2]]['quantity'] = product_quantity_group_by[serial[2]]['quantity'] + 1
            pulled_serials.append({
                "serial_number": serial[0],
                "serial_code": result,
                'product_id': serial[2],
                'product_name': serial[3],
                'SKU': serial[4],
                'expiry_date': datetime.strftime(serial[5], DATETIME_FORMAT) if serial[5] else None,
                'value': serial[6],
                'pin_code': serial[7],
                'is_prepaid': product.is_prepaid,
                'price': invite.price,
            })
        res["order"] = order.name
        res["pulled_serials"] = pulled_serials

        if invite.merchant.partner_id.balance < deducted_balance:
            raise UserError("Not Enough Balance")
        invite.merchant.partner_id.balance = invite.merchant.partner_id.balance - deducted_balance
        invite.deduct_balance(deducted_balance, product_quantity_group_by)
        return res

    @staticmethod
    def get_serial_status(status):
        if status == '1':
            return 'Available'
        if status == '2':
            return 'Reserved'
        if status == '3':
            return 'Pulled'
        if status == '5':
            return 'Redeemed'
        if status == '4':
            return 'Expired'

    @http.route(
        "/exposed/order_list",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def order_list(self, **kw):
        if not request.env.user.is_merchant:
            raise AccessDenied()
        if request.env.user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["3"], user=request.env.user)
            orders = PullController.order_list_func(kw, request.env.user.parent_merchant)
        else:
            orders = PullController.order_list_func(kw, request.env.user)
        return BaseController._create_response(orders)

    @http.route(
        "/exposed/order_list_online",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def order_list_online(self, **kw):
        user = BaseController.key_authenticate(kw)
        if not user or not user.is_merchant:
            raise AccessDenied()
        orders = PullController.order_list_func(kw, user)
        return BaseController._create_response(orders)

    @staticmethod
    def order_list_func(kw, user):
        if not user.is_merchant:
            raise UserError("Invalid Request")
        validated = BaseController.get_validated(
            kw,
            {"name": "string", "offset": "int", "limit": "int", "id": "number",
             "product_name": "string", "order_date": "string"},
        )
        domain = [('partner_id', '=', user.partner_id.id)]
        name = validated.get("name")
        id = validated.get("id")
        offset = validated.get('offset')
        limit = validated.get("limit")
        product_name = validated.get('product_name')
        order_date = validated.get('order_date')

        if name:
            domain += [('name', 'ilike', name)]
        if id:
            domain += [("id", '=', id)]
        if product_name:
            domain += [('order_line.product_id.name', 'ilike', product_name)]
        if order_date:
            domain += [
                ('date_order', '>=', datetime.strftime(datetime.strptime(order_date, "%Y-%m-%d"), DATETIME_FORMAT)),
                ('date_order', '<', datetime.strftime(datetime.strptime(order_date, "%Y-%m-%d")
                                                      + timedelta(days=1), DATETIME_FORMAT))]

        orders = request.env['sale.order'].sudo().search(domain, limit=limit, offset=offset,
                                                         order="create_date desc")
        count = request.env['sale.order'].sudo(1).search_count(domain)
        data = []
        for p in orders:
            data.append({
                'name': p.name,
                "id": p.id,
                'date': datetime.strftime(p.date_order, DATETIME_FORMAT) if p.date_order else None,
                'product_id': p.order_line.product_id.id,
                'product_name': p.order_line.product_id.name,
                'price': p.order_line.price_unit,
                'amount_total': p.amount_total,
                'pulled_serials': p.get_pulled_serials() if id else []
            })
        res = {'data': data, 'totalCount': count}
        return res

    @http.route(
        "/exposed/create_invoice_request",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_invoice_request(self, **kw):
        user = request.env.user
        if not user or not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"merchant_reference": "string|required", "from_date": "string", "to_date": "string"},
        )
        invite = request.env['merchant.package.invites'].with_user(1).search(
            [('merchant.reference', '=', validated['merchant_reference']),
             ('product.service_provider_id', '=', request.uid)
             ])
        if not invite:
            raise UserError("Merchant Not Invited")

        order = request.env['merchant.invoice.request'].sudo().create({
            'service_provider_id': request.uid,
            'merchant': invite.merchant.id,
            'from_date': datetime.strptime(validated['from_date'], DATE_FORMAT) if validated['from_date'] else None,
            'to_date': datetime.strptime(validated['to_date'], DATE_FORMAT) if validated['from_date'] else None,
            'type': 'sp'
        })
        return BaseController._create_response(data=order.serialize_for_api())

    @http.route(
        "/exposed/get_invoice_request_list",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_invoice_request_list(self, **kw):
        user = request.env.user
        if not user or not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"merchant_reference": "string", 'limit': "number", "offset": "number", "type": "string"},
        )

        domain = [('service_provider_id', '=', request.uid)]
        merchant_reference = validated.get("merchant_reference")
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get("limit") else 20
        type = validated.get("type")
        if merchant_reference:
            domain += [("merchant.reference", '=', merchant_reference)]
        if type:
            domain.append(('type', '=', type))
        inv_requests = request.env['merchant.invoice.request'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                                   order="request_date desc")
        request_count = request.env['merchant.invoice.request'].with_user(1).search_count(domain)
        data = []
        for invoice_request in inv_requests:
            data.append(invoice_request.serialize_for_api())
        res = {
            'data': data,
            'totalCount': request_count
        }
        return BaseController._create_response(data=res)

    @http.route(
        "/exposed/toggle_show_on_merchant_dashboard",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def toggle_show_on_merchant_dashboard(self, **kw):
        user = request.env.user
        if not user or not user.is_service_provider:
            raise AccessDenied()

        validated = BaseController.get_validated(
            kw,
            {"id": "number"},
        )
        invoice = request.env['merchant.invoice.request'].sudo().search([('id', '=', validated['id'])])
        if not invoice or invoice.state != 'success' and invoice.service_provider_id.id != request.uid:
            raise UserError("Invoice Not Found")
        invoice.show_on_merchant_dashboard = not invoice.show_on_merchant_dashboard
        return BaseController._create_response("ok", message='show on merchant dashboard flag toggled successfully')

    @http.route(
        "/exposed/get_merchant_invoices",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_merchant_invoices(self, **kw):
        user = request.env.user
        if not user or not user.is_merchant:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {'limit': "number", "offset": "number", "date": "string", "type": "string"},
        )
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get("limit") else 20
        date = validated.get("date")
        type = validated.get("type")
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["5"], user=request.env.user)
            domain = [('show_on_merchant_dashboard', '=', True), ('merchant', '=', user.parent_merchant.id)]
        else:
            domain = [('show_on_merchant_dashboard', '=', True), ('merchant', '=', request.uid)]
        if date:
            domain.append(('date', '>=', date))
        if type:
            if type == "sp" or type == "system":
                domain.append(('type', '=', type))

        inv_requests = request.env['merchant.invoice.request'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                                   order="request_date desc")
        request_count = request.env['merchant.invoice.request'].with_user(1).search_count(domain)
        data = []
        for invoice_request in inv_requests:
            data.append(invoice_request.serialize_for_api())
        res = {
            'data': data,
            'totalCount': request_count
        }
        return BaseController._create_response(data=res)

    @http.route(
        "/exposed/download_attachment",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_attachment(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'invoice')]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain, limit=1)
        invoice_request = request.env['merchant.invoice.request'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        filename = 'Invoice %s - %s - %s.pdf' % (
            invoice_request.merchant.name, invoice_request.from_date, invoice_request.to_date)
        file = requests.get(attach.url, timeout=5)
        if file:
            content = file.content
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content)),
                              ('Content-Disposition', content_disposition(filename))
                              ]
            return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()
