import logging
from datetime import datetime
from odoo import _, SUPERUSER_ID
import json
from odoo import http, SUPERUSER_ID
from odoo.http import request,route
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied
from hashlib import sha256
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT


class CheckCodesController(BaseController):
    @http.route(
        "/exposed/upload_check_code_batch",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def upload_check_code_batch(self, **kw):
        user = request.env.users
        if not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()
        validated = self.get_validated(kw, {
            'codes': "list"
        })
        batch_request = request.env['batch.check.codes.request'].with_user(1).create({
            'request_date': datetime.now(),
            'user_id': request.uid,
        })
        for code in validated['codes']:
            new_serial = batch_request.serials.new({
                'serial_code': code,
            })
            batch_request.serials += new_serial
        return BaseController._create_response("ok")

    @http.route(
        "/exposed/get_check_code_batches",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_check_code_batchs(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = self.get_validated(kw,
            {"offset": "int", "limit": "int", "date": "string"},
        )
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get("limit") else 20
        date = validated.get("date")
        domain = [('user_id', '=', request.uid)]
        if date:
            domain.append(('date', '=', date))
        requests = request.env['batch.check.codes.request'].with_user(1).search(domain, limit=limit, offset=offset)
        count = request.env['batch.check.codes.request'].with_user(1).search_count(domain)
        data = [item.serialize_for_api() for item in requests]
        return BaseController._create_response({'data': data, 'totalCount': count})

    @http.route(
        "/exposed/download_batch_result",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_batch_result(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = self.get_validated(kw, {
            "id": "number|required"
        })
        id = validated.get('id')
        domain = [('user_id', '=', request.uid), ('id', '=', id), ('state', '=', 'success')]

        batch_request = request.env['batch.check.codes.request'].with_user(1).search(domain)
        if not batch_request:
            raise UserError("Batch Request Not Found")
        serials = [item.serialize_for_api() for item in batch_request.serials]
        return BaseController._create_response(serials)

    @route("/exposed/check_balance_prepaid",
           type="json",
           auth="none",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False)
    @BaseController.with_errors
    def check_balance_prepaid_online(self, **kw):
        user = BaseController.key_authenticate(kw)
        if (not user or not (user.is_service_provider or user.is_merchant)):
            raise AccessDenied()
        product_code_result = CheckCodesController.check_balance_prepaid(kw, user)
        return BaseController._create_response(product_code_result, 200, _("Code Already Found"))

    @route("/exposed/check_balance_prepaid_offline",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def check_balance_prepaid_offline(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if (not user or not (user.is_service_provider or user.is_merchant)):
            raise AccessDenied()
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["4"], user=user)
            product_code_result = CheckCodesController.check_balance_prepaid(kw, user.parent_merchant.id)
        else:
            product_code_result = CheckCodesController.check_balance_prepaid(kw, user)
        return BaseController._create_response(product_code_result, 200, _("Code Already Found"))

    @staticmethod
    def check_balance_prepaid(kw, user):
        dic_lines, language = BaseController.get_validated(kw,
                                                           {
                                                               "lines": "list|required",
                                                               "language": "string",
                                                           }).values()
        lines = []
        for line in dic_lines:
            validated = BaseController.get_validated(
                line,
                {
                    "code": "required|string",
                    "pin_code": "required|string"
                },
                req_only=True
            )
            lines.append(validated)

        if len(lines) == 0:
            raise UserError("Lines Are Empty")

        product_code_result_list = []
        for item in lines:
            real_code = item["code"]
            pin_code = item["pin_code"]
            code = str(item["code"]).replace(" ", "").replace("-", "")
            aes_cipher = request.env['aes.cipher'].sudo().create([])
            # product_serial = request.env['product.serials'].sudo().search([
            #     ('pin_code', '=', item["pin_code"])
            # ]).filtered(lambda l: aes_cipher.decrypt(l.serial_code) == code )
            serial_code_has = sha256(code.encode('utf-8')).hexdigest()
            domain = [
                "|", ('serial_code_hash', "=", serial_code_has), ('serial_number', '=', real_code),
                ('pin_code', '=', pin_code),
            ]
            product_serial = request.env['product.serials'].sudo().search(domain)
            if len(product_serial) == 0 or not product_serial.product_id.is_prepaid:
                product_code_result_list.append({
                    'serial': item["code"],
                    'pin_code': item["pin_code"],
                    'found': False,
                    'expired': False,
                    'expiry_date': False
                })
                continue
            if (product_serial.expiry_date and product_serial.expiry_date < datetime.now().date()) \
                or product_serial.state == '4':
                product_code_result_list.append({
                    'serial': item["code"],
                    'pin_code': item["pin_code"],
                    'found': True,
                    'expired': True,
                    'expiry_date': datetime.strftime(product_serial.expiry_date,
                                                          DATETIME_FORMAT) if product_serial.expiry_date else None
                })
                continue

            def starts_email(email_id):
                email = email_id
                # Find the index of the @ symbol
                at_index = email.index("@")
                # Slice the string to get the first three characters
                first_three = email[:3]
                # Replace the remaining characters with asterisks
                remaining = "*" * (at_index - 3)
                # Concatenate the first three characters and the asterisks up to the @ symbol with "@gmail"
                masked_email = first_three + remaining + email[at_index:]
                return masked_email

            product = product_serial.product_id
            voucher_secret = {}
            for field in json.loads(product.voucher_secret):
                value = field["value"]
                if field["value"] and field['type'] == '2':
                    value = int(value)
                if field['type'] == '3':
                    value = bool(value)
                voucher_secret[field['name'].upper()] = value
            product_code_result = {
                'name': product.name if language == 'en' else product.name_ar,
                'product_name': product_serial.product_id.name if language == 'en' else product_serial.product_id.name_ar,
                'pin_code': product_serial.pin_code,
                'found': True,
                'expired': datetime.now().date() >= product_serial.expiry_date if product_serial.expiry_date else False,
                'expiry_date': datetime.strftime(product_serial.expiry_date, DATETIME_FORMAT) if product_serial.expiry_date else False,
                'code': real_code,
                'email_id': starts_email(product_serial.email_id),
                'image': product_serial.product_id.get_product_image_url(),
                'voucher_type': product_serial.product_id.voucher_type_id.name.upper() if product.voucher_type_id else "VOUCHER",
                'voucher_secret': voucher_secret,
                'how_to_use': product.how_to_use if product.how_to_use else "",
                'how_to_use_ar': product.how_to_use_ar if product.how_to_use_ar else "",
                'state': product_serial.state,
                # "is_redeemed": product_serial.state == 'redeemed',
                'vendor': product.service_provider_id.name.upper() if product.service_provider_id else "REDEEMLY",
                'balance': product_serial.value,
                'redeem_history': [
                    {
                        'redeem_item': {
                            'id': line.id,
                            'value': line.value,
                            'user_id': line.user_id[:2] + "*" * (len(line.user_id) - 4) + line.user_id[-2:],
                            'transaction_id': line.transaction_id,
                            'date': datetime.strftime(line.date, DATETIME_FORMAT) if line.date else None,
                        }
                    }
                    for line in product_serial.redeem_history_prepaid_ids
                ]
            }
            product_code_result_list.append(product_code_result)
        return product_code_result_list