import logging
from datetime import datetime
from hashlib import sha256

from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.addons.redeemly_pin_management.controllers.product_controller import ProductController
from odoo.http import request
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.addons.redeemly_pin_management.services.redeem_service import RedeemService
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied
from psycopg2.errors import UniqueViolation
from odoo import _


class RedeemController(BaseController):
    @http.route("/exposed/redeem",
                type="json",
                auth="jwt_dashboard",
                save_session=False,
                cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def redeem_jwt(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        return self.redeem_func(kw, user)

    @http.route(
        "/exposed/redeem_online",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def redeem_online(self, **kw):
        user = BaseController.key_authenticate(kw, is_redeem_online=True)
        return self.redeem_func(kw, user)

    @http.route(
        "/exposed/redeem_with_hash",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def redeem_with_hash(self, **kw):
        if not kw.get('sp_hash') or not isinstance(kw.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', kw.get('sp_hash'))])
        return self.redeem_func(kw, user)

    @staticmethod
    def redeem_func(kw, user):
        if not user or not user.is_service_provider:
            raise AccessDenied()
        running_op = None
        try:
            code, email, reference_user_id, transaction_id, \
                language, deduct_value, is_prepaid, \
                product_type, pin_code, secret, sku, product_attribute_values, \
                branch_id, business_reference, discount_amount, mobile_country_code, \
                customer_mobile_number, order_id = BaseController.get_validated(kw, {
                "code": "required|string",
                "email": "string",
                "user_id": "string",
                'transaction_id': "string",
                "language": "string",
                "deduct_value": "number",
                "is_prepaid": "boolean",
                "product_type": "string",
                "pin_code": "string",
                "secret": "string",
                "sku": "string",
                "product_attribute_values": "list",
                "branch_id": "string",
                "business_reference": "string",
                "discount_amount": "number",
                "mobile_country_code": "string",
                "customer_mobile_number": "string",
                "order_id": "string",
            }).values()
            # validate input
            if user.codes_additional_value == 'secret' and not secret:
                raise UserError("Secret Required")

            # validate code format
            if is_prepaid or product_type == 'prepaid':
                is_prepaid = True
                product_type = 'prepaid'

            if product_type == 'mask':
                code = RedeemService.validate_code(code)

            if is_prepaid:
                if not code or not reference_user_id or not transaction_id or not deduct_value or not pin_code:
                    raise UserError(
                        "You Must Type the Following Params : code  user_id , transaction_id , deduct_value , pin_code")

            running_op = request.env["running.ops"].with_user(1).add_entry({
                "type": "redeem",
                "unique_val": code
            })
            redeemly_code = RedeemService.get_code(code, product_type, reference_user_id, user, pin_code, secret)
            if redeemly_code.expiry_date and redeemly_code.expiry_date < datetime.now().date():
                if running_op:
                    request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                return BaseController._create_response({}, 400, _("Code Expired."))
            if sku and redeemly_code.product_id.SKU != sku:
                logging.info('sku====== %s', sku)
                if running_op:
                    request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                return BaseController._create_response({}, 400, _("Code Not Found."))
            if not redeemly_code:
                logging.info('redeemly_code====== %s', redeemly_code)
                if running_op:
                    request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                return BaseController._create_response({}, 400, _("Code Not Found."))
            if redeemly_code.product_id.service_provider_id.id != user.id:
                logging.info('redeemly_code.product_id.service_provider_id.id ====== %s',
                             redeemly_code.product_id.service_provider_id.id)
                logging.info('user.id====== %s', user.id)
                if running_op:
                    request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                return BaseController._create_response({}, 400, _("Code Not Found."))

            auth_key = request.httprequest.headers.get('Authorization')
            website_api_key_id = user.website_key_ids.filtered(
                lambda l: l.website_redeemly_api_key == auth_key)

            if is_prepaid:
                redeemly_code.user_id = reference_user_id
                redeemly_code.transaction_id = transaction_id
                if deduct_value > 0 and (redeemly_code.value - deduct_value >= 0):
                    redeemly_code.value -= deduct_value
                    att_values = []
                    att_values = RedeemController.get_attribute_value_list(redeemly_code, product_attribute_values)
                    redeemly_history = request.env['redeem.history.prepaid'].with_user(1).create(
                        [
                            {
                                'product_serial': redeemly_code.id,
                                'value': deduct_value,
                                'date': datetime.now().date(),
                                'user_id': reference_user_id,
                                'transaction_id': transaction_id,
                                'website_api_key_id': website_api_key_id.id,
                                'product_attributes_value': att_values
                            }
                        ]
                    )
                elif deduct_value <= 0:
                    if running_op:
                        request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                    return BaseController._create_response({}, 400, _("Invalid deduct value."))
                elif redeemly_code.value - deduct_value < 0:
                    if running_op:
                        request.env["running.ops"].with_user(1).remove_entry(running_op.id)
                    return BaseController._create_response({}, 400, _("No enough balance."))

            redeem_result = RedeemService.get_redeem_result(redeemly_code, product_type, deduct_value, language)

            RedeemService.redeem(redeemly_code, product_type)

            is_redeemed = redeem_result["is_redeemed"]
            if not is_prepaid and is_redeemed == '3' and redeemly_code.state == '5':
                att_values = []
                att_values = RedeemController.get_attribute_value_list(redeemly_code, product_attribute_values)
                redeemly_history = request.env['redeem.history.prepaid'].with_user(1).create(
                    [
                        {
                            'product_serial': redeemly_code.id,
                            'value': 0,
                            'date': datetime.now().date(),
                            'user_id': reference_user_id,
                            'email_sent': True if user.codes_additional_value in ['email_with_redeem',
                                                                                  'net_dragon'] else False,
                            'product_attributes_value': att_values,
                            'website_api_key_id': website_api_key_id.id,
                        }
                    ]
                )

            if running_op:
                request.env["running.ops"].with_user(1).remove_entry(running_op.id)

            return BaseController._create_response(redeem_result, 200, RedeemService.get_message(language, is_redeemed))
        except Exception as ex:
            if isinstance(ex, UniqueViolation):
                return BaseController._create_response({}, 400, _("Another operation is running. please wait"))
            request.env.cr.rollback()
            if running_op:
                request.env["running.ops"].with_user(1).remove_entry(running_op.id)
            return BaseController._create_response({}, 400, str(ex))

    @staticmethod
    def get_attribute_value_list(code, product_attribute_values):
        attributes = request.env['product.template'].with_user(1).search(
            [('id', '=', code.product_id.id)]).attribute_definition_ids
        required_ids = attributes.filtered(lambda v: v.required == True).ids
        if len(required_ids) == 0 and not product_attribute_values:
            return
        processed_ids = []
        res = []
        for value in product_attribute_values:
            current_att = attributes.filtered(lambda v: v.id == value['id'])
            if not current_att:
                continue
            processed_ids.append(current_att.id)
            res.append((0, 0, {
                "name": current_att.name,
                "type": current_att.type,
                "required": current_att.required,
                "product_id": current_att.product_id.id,
                "value": value['value']
            }))
        if not all(item in processed_ids for item in required_ids):
            raise UserError("Missing Required Attributes Values")
        return res

    @http.route(
        "/exposed/check_and_redeem_with_hash",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check_and_redeem_with_hash(self, **kw):
        validated = BaseController.get_validated(kw, {"codes": "list|required", 'sp_hash': 'string|required',
                                                      'sku': 'string'})

        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validated['sp_hash'])])
        return self.check_code_with_hash_func(user=user, param=validated)
        # return ProductController.check_balance_prepaid(kw, user)

    @http.route(
        "/exposed/check_and_redeem",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check_codes(self, **kw):
        validated = BaseController.get_validated(kw, {"codes": "list|required"})
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        return self.check_code_func(user=user, param=validated)

    @staticmethod
    @BaseController.with_errors
    def check_code_func(user, param):
        if not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()
        result = []
        if len(param['codes']) > 20:
            raise UserError("Excess limit 20")
        for validated_serial in param["codes"]:
            serial = request.env['product.serials'].with_user(1).search(
                ['|', ('serial_code_hash', '=', sha256(validated_serial.encode('utf-8')).hexdigest()),
                 ('serial_number', '=', validated_serial)
                 ])

            if (not serial) or (user.is_service_provider and serial.product_id.service_provider_id.id != user.id) \
                    or (user.is_merchant and serial.pulled_by.id != user.id):
                result.append({
                    'serial': validated_serial,
                    'found': False,
                    'expired': False,
                    'expiry_date': False
                })
                continue
            if (serial.expiry_date and serial.expiry_date < datetime.now().date()) or serial.state == '4':
                result.append({
                    'serial': serial.serial_number,
                    'found': True,
                    'expired': True,
                    'image': serial.product_id.get_product_image_url(),
                    'name': serial.product_id.name,
                    'expiry_date': datetime.strftime(serial.expiry_date,
                                                     DATETIME_FORMAT) if serial.expiry_date else None,

                })
                continue
            serial.check_count = serial.check_count + 1
            redeem_result = {
                'name': serial.product_id.name,
                'product_type': 'prepaid' if serial.product_id.is_prepaid else 'serial',
                'serial': serial.serial_number,
                'state': serial.state,
                'is_redeemed': True if serial.state == '5' else False,
                'found': True,
                'expired': datetime.now().date() >= serial.expiry_date if serial.expiry_date else False,
                'expiry_date': datetime.strftime(serial.expiry_date, DATETIME_FORMAT) if serial.expiry_date else False,
                'image': serial.product_id.get_product_image_url(),
                'pulled_by': serial.pulled_by.id,
                'pulled_by_reference': serial.pulled_by.reference,
                'pulled_by_name': serial.pulled_by.name,
                'pull_date': datetime.strftime(serial.pull_date,
                                               DATETIME_FORMAT) if serial.pull_date else None,

                'how_to_use': serial.product_id.how_to_use,
                'how_to_use_ar': serial.product_id.how_to_use_ar,
                "check_count": serial.check_count,
                "last_check_time": datetime.strftime(serial.last_check_time,
                                                     DATETIME_FORMAT) if serial.last_check_time else None,
                'vendor': serial.product_id.service_provider_id.name.upper() if serial.product_id.service_provider_id else "SKARLA",
                "distributor": serial.distributor if serial.distributor else '',
                "country_of_generation_parameters": serial.country_of_generation_parameters if serial.country_of_generation_parameters else ''
            }

            result.append(redeem_result)
            serial.last_check_time = datetime.now()
        return BaseController._create_response(result)

    @staticmethod
    @BaseController.with_errors
    def check_code_with_hash_func(user, param, required_sku=True):
        if not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()
        result = []
        if len(param['codes']) > 20:
            raise UserError("Excess limit 20")

        for validated_serial in param["codes"]:
            if user.codes_additional_value == 'secret' and 'secret' not in validated_serial:
                raise UserError("secret required")
            domain = ['|', ('serial_code_hash', '=', sha256(validated_serial['code'].encode('utf-8')).hexdigest()),
                      ('serial_number', '=', validated_serial['code'])]
            sku_required = required_sku
            if user.codes_additional_value == 'secret':
                domain = ['&', '|',
                          ('serial_code_hash', '=', sha256(validated_serial['code'].encode('utf-8')).hexdigest()),
                          ('serial_number', '=', validated_serial['code']),
                          ('secret_value', '=', validated_serial['secret'])]
                # sku_required = False
            serial = request.env['product.serials'].with_user(1).search(domain)

            if serial and sku_required and serial.product_id.SKU != param.get('sku'):
                result.append({
                    'serial': validated_serial['code'],
                    'found': False,
                    'expired': False,
                    'expiry_date': False
                })
                continue

            if (not serial) or (user.is_service_provider and serial.product_id.service_provider_id.id != user.id) \
                    or (user.is_merchant and serial.pulled_by.id != user.id):
                result.append({
                    'serial': validated_serial['code'],
                    'found': False,
                    'expired': False,
                    'expiry_date': False
                })
                continue
            if (serial.expiry_date and serial.expiry_date < datetime.now().date()) or serial.state == '4':
                result.append({
                    'serial': serial.serial_number,
                    'found': True,
                    'expired': True,
                    'image': serial.product_id.get_product_image_url(),
                    'name': serial.product_id.name,
                    'expiry_date': datetime.strftime(serial.expiry_date,
                                                     DATETIME_FORMAT) if serial.expiry_date else None,

                })
                continue
            serial.check_count = serial.check_count + 1
            redeem_result = {
                'name': serial.product_id.name,
                "sku": serial.product_id.SKU,
                'product_specific_attribute': serial.product_id.product_specific_attribute,
                'product_currency': serial.product_id.product_currency.name,
                'product_amount': serial.product_id.product_amount,
                'product_type': 'prepaid' if serial.product_id.is_prepaid else 'serial',
                'serial': serial.serial_number,
                'is_redeemed': True if serial.state == '5' else False,
                'found': True,
                'expired': datetime.now().date() >= serial.expiry_date if serial.expiry_date else False,
                'expiry_date': datetime.strftime(serial.expiry_date, DATETIME_FORMAT) if serial.expiry_date else False,
                'image': serial.product_id.get_product_image_url(),
                'pulled_by': serial.pulled_by.id,
                'pulled_by_reference': serial.pulled_by.reference,
                'pulled_by_name': serial.pulled_by.name,
                'pull_date': datetime.strftime(serial.pull_date,
                                               DATETIME_FORMAT) if serial.pull_date else None,

                'how_to_use': serial.product_id.how_to_use,
                'how_to_use_ar': serial.product_id.how_to_use_ar,
                "check_count": serial.check_count,
                "last_check_time": datetime.strftime(serial.last_check_time,
                                                     DATETIME_FORMAT) if serial.last_check_time else None,
                'vendor': serial.product_id.service_provider_id.name.upper() if serial.product_id.service_provider_id else "SKARLA",
                "distributor": serial.distributor if serial.distributor else '',
                "country_of_generation_parameters": serial.country_of_generation_parameters if serial.country_of_generation_parameters else ''

            }

            result.append(redeem_result)
            serial.last_check_time = datetime.now()
        return BaseController._create_response(result)

    @http.route(
        "/exposed/check_and_redeem_online",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check_and_redeem_online(self, **kw):
        user = BaseController.key_authenticate(kw, is_redeem_online=True)
        if not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()

        validated = BaseController.get_validated(kw, {"codes": "list|required"})

        result = []
        if len(validated['codes']) > 20:
            raise UserError("Excess limit 20")
        for validated_serial in validated["codes"]:
            serial = request.env['product.serials'].with_user(1).search(
                ['|', ('serial_code_hash', '=', sha256(validated_serial.encode('utf-8')).hexdigest()),
                 ('serial_number', '=', validated_serial)
                 ])

            if (not serial) or (user.is_service_provider and serial.product_id.service_provider_id.id != user.id) \
                    or (user.is_merchant and serial.pulled_by.id != user.id):
                result.append({
                    'serial': validated_serial,
                    'found': False,
                    'expired': False,
                    'expiry_date': False
                })
                continue
            if (serial.expiry_date and serial.expiry_date < datetime.now().date()) or serial.state == '4':
                result.append({
                    'serial': serial.serial_number,
                    'found': True,
                    'expired': True,
                    'expiry_date': datetime.strftime(serial.expiry_date,
                                                     DATETIME_FORMAT) if serial.expiry_date else None,

                })
                continue
            serial.check_count = serial.check_count + 1
            redeem_result = {
                'name': serial.product_id.name,
                'product_type': 'prepaid' if serial.product_id.is_prepaid else 'serial',
                'serial': serial.serial_number,
                'found': True,
                'is_redeemed': True if serial.state == '5' else False,
                'expired': datetime.now().date() >= serial.expiry_date if serial.expiry_date else False,
                'expiry_date': datetime.strftime(serial.expiry_date, DATETIME_FORMAT) if serial.expiry_date else False,
                'image': serial.product_id.get_product_image_url(),
                'pulled_by': serial.pulled_by.id,
                'pulled_by_reference': serial.pulled_by.reference,
                'pulled_by_name': serial.pulled_by.name,
                'pull_date': datetime.strftime(serial.pull_date,
                                               DATETIME_FORMAT) if serial.pull_date else None,
                'how_to_use': serial.product_id.how_to_use,
                'how_to_use_ar': serial.product_id.how_to_use_ar,
                "check_count": serial.check_count,
                "last_check_time": datetime.strftime(serial.last_check_time,
                                                     DATETIME_FORMAT) if serial.last_check_time else None,
                'vendor': serial.product_id.service_provider_id.name.upper() if serial.product_id.service_provider_id else "SKARLA",

                "distributor": serial.distributor if serial.distributor else '',
                "country_of_generation_parameters": serial.country_of_generation_parameters if serial.country_of_generation_parameters else ''

            }

            result.append(redeem_result)
            serial.last_check_time = datetime.now()
        return BaseController._create_response(result)

    @http.route(
        "/exposed/get_prepaid_redeem_history",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_prepaid_redeem_history(self, **kw):
        validated = BaseController.get_validated(kw, {"code": "string|required", "limit": "number", "offset": "number"})
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get('limit') if validated.get('limit') else 20
        user = request.env.user
        if not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()
        exist = request.env['product.serials'].with_user(1).search(
            ['|', ('serial_code_hash', '=', sha256(validated['code'].encode('utf-8')).hexdigest()),
             ('serial_number', '=', validated['code'])
             ])
        res = {
            "serial": exist.serialize_for_api(),
            "history": {
                "data": [],
                "totalCount": 0
            }
        }
        if not exist or (user.is_service_provider and exist.product_id.service_provider_id.id != user.id) \
                or (user.is_merchant and exist.pulled_by.id != user.id):
            raise UserError("Code Not Found")
        data = request.env['redeem.history.prepaid'].with_user(1).search([('product_serial', '=', exist.id)],
                                                                         limit=limit, offset=offset, order='id desc')
        res['history']['data'] = [item.serialize_for_api() for item in data]
        count = request.env['redeem.history.prepaid'].with_user(1).search_count([('product_serial', '=', exist.id)])
        res['history']['totalCount'] = count
        return BaseController._create_response(res)

    @http.route(
        "/exposed/get_prepaid_redeem_history_online",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_prepaid_redeem_history_online(self, **kw):
        user = BaseController.key_authenticate(kw)
        if not user or not (user.is_service_provider or user.is_merchant):
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {"code": "string|required", "limit": "number", "offset": "number"})
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get('limit') if validated.get('limit') else 20
        exist = request.env['product.serials'].with_user(1).search(
            ['|', ('serial_code_hash', '=', sha256(validated['code'].encode('utf-8')).hexdigest()),
             ('serial_number', '=', validated['code'])
             ])
        res = {
            "serial": exist.serialize_for_api(),
            "history": {
                "data": [],
                "totalCount": 0
            }
        }
        if not exist or (user.is_service_provider and exist.product_id.service_provider_id.id != user.id) \
                or (user.is_merchant and exist.pulled_by.id != user.id):
            raise UserError("Code Not Found")
        data = request.env['redeem.history.prepaid'].with_user(1).search([('product_serial', '=', exist.id)],
                                                                         limit=limit, offset=offset)
        res['history']['data'] = [item.serialize_for_api() for item in data]
        count = request.env['redeem.history.prepaid'].with_user(1).search_count([('product_serial', '=', exist.id)])
        res['history']['totalCount'] = count
        return BaseController._create_response(res)

    @http.route(
        "/exposed/get_redemption_history",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_redemption_history(self, **kw):
        user = request.env.user
        if not user and not user.is_service_provider:
            raise AccessDenied()

        validated = BaseController.get_validated(
            kw,
            {
                "serial": "string",
                "limit": "number",
                "offset": "number",
                "id": "number"
            }
        )
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        serial = validated.get('serial')
        id = validated.get('id')
        domain = [('product_serial.product_id.service_provider_id', '=', user.id)]
        if serial:
            domain.append(('product_serial.serial_number', '=', serial))
        if id:
            domain.append(('id', '=', id))
        history = request.env['redeem.history.prepaid'].sudo().search(domain, limit=limit, offset=offset,
                                                                      order='id desc')
        history_count = request.env['redeem.history.prepaid'].sudo().search_count(domain)
        res = {'data': [item.serialize_for_api() for item in history], 'totalCount': history_count}
        return BaseController._create_response(data=res)
