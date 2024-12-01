import hmac
import hashlib
import string
from odoo.http import request
import requests

from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
import json
from odoo.tools.config import config
from odoo.addons.redeemly_pin_management.controllers.redeem_controller import RedeemController
from odoo.exceptions import UserError, AccessDenied
from random import randint


# NETDRAGON_API = {
#     "Tokens_100": "/HmallReseller/api/HeApi",
#     "CPS_60": "/HmallReseller/api/EncoApi",
#     "EPS_80": "/HmallReseller/api/EoApi",
#     # "CPS_60": "/HmallReseller/api/YdcoApi",
# }


class NetDragonController(BaseController):
    @staticmethod
    def check_service_provider_signature(kw):
        key = request.httprequest.headers.get('Authorization')
        message = key + kw.get('nonce')
        secret = config.get('net_dragon_redemption_portal_secret')
        temp = hmac.new(
            bytes(secret, 'latin-1'),
            msg=bytes(message, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        if temp != kw.get('signature'):
            raise UserError("Invalid Request")

    @staticmethod
    def check_redemption_portal_signature_for_validate(signature, product_id, nonce, sp_hash, user_id, zone_id, ):
        message = str(product_id) + nonce + sp_hash + user_id + zone_id
        secret = config.get('net_dragon_redemption_portal_secret')
        temp = hmac.new(
            bytes(secret, 'latin-1'),
            msg=bytes(message, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        if temp != signature:
            raise UserError("Invalid Request")

    @http.route(
        "/net_dragon/get_server_list",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    def get_server_list(self, **kw):
        validated = BaseController.get_validated(kw, {
            "category_id": "number|required"
        })
        category = request.env['netdragon.product.category'].sudo().search([('id', '=', validated['category_id'])])
        if not category:
            raise UserError("Product Category Not Defined")

        endpoint = config.get("net_dragon_base_url") + category.endpoint
        body = {

        }
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(body)
        response = requests.request(
            "GET", endpoint + "/serverlist", headers=headers, data=payload)
        res = json.loads(response.text)

        return BaseController._create_response({'data': res, 'totalCount': len(res['serverList'])})

    @http.route(
        "/net_dragon/get_sp_products",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    def get_sp_products(self, **kw):
        validated = BaseController.get_validated(kw, {
            "nonce": "string|required",
            "limit": "number",
            "offset": "number",
            "signature": "string|required",
            "product_specific_attribute": "string",
            "product_id": "number",
            "category_id": "number"
        })
        self.check_service_provider_signature(kw)
        user = BaseController.key_authenticate(kw)
        if not user.is_service_provider:
            raise AccessDenied()
        if not user.netdragon_account_name or not user.netdragon_account_secret:
            raise UserError("Invalid Request")

        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get('limit') else 8
        product_specific_attribute = validated.get('product_specific_attribute')
        product_id = validated.get('product_id')
        category_id = validated.get('category_id')
        domain = [('service_provider_id', '=', user.id)]
        if product_id:
            domain.append(('id', '=', product_id))
        if category_id:
            domain.append(('netdragon_product_category', '=', category_id))
        if product_specific_attribute:
            domain.append(('product_specific_attribute', '=', product_specific_attribute))

        products = request.env['product.template'].with_user(1).search(domain, limit=limit, offset=offset)

        res = [
            product.serialize_for_api()
            for product in products
        ]

        count = request.env['product.template'].with_user(1).search_count(domain)

        return BaseController._create_response({'data': res, 'totalCount': count})

    @http.route(
        "/net_dragon/verify",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def net_dragon_verify_account(self, **kw):
        validate = BaseController.get_validated(kw, {
            "product_id": "number|required",
            "signature": "string|required",
            "nonce": "string|required",
            "sp_hash": "string|required",
            "user_id": "string|required",
            "zone_id": "string",
        })
        if not validate.get('sp_hash') or not isinstance(validate.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validate.get('sp_hash'))])
        if not user:
            raise AccessDenied()

        service_provider_id = user.netdragon_account_name
        service_provider_secret = user.netdragon_account_secret
        product = request.env['product.template'].sudo().search([('id', '=', validate["product_id"])])
        if product.product_specific_attribute != 'topup':
            raise UserError("Invalid Request")

        self.check_redemption_portal_signature_for_validate(validate.get('signature'), validate.get('product_id'),
                                                            validate.get('nonce'), validate.get('sp_hash'),
                                                            validate.get('user_id'), validate.get('zone_id'),
                                                            )

        log = {
            'username': validate["user_id"],
        }

        taxId = str(randint(100000, 999999999999999))
        validation_request, validation_response = \
            self.call_net_dragon_validate(service_provider_id, validate.get('user_id'), validate.get('zone_id'),
                                          product.product_currency.name, product.product_amount,
                                          product, taxId,
                                          service_provider_secret
                                          )
        try:
            log["validate_request_body"] = validation_request
            log["validate_response_result"] = validation_response
            if validation_response and validation_response.get("error"):
                raise UserError("User Not Found")

            log["our_message"] = validation_response.get("result")["username"]
            request.env['netdragon.log'].sudo().create(log)
            return BaseController._create_response(data={}, message=log["our_message"])

        except Exception as e:
            request.env.cr.rollback()
            log["our_message"] = str(e)
            request.env['netdragon.log'].sudo().create(log)
            request.env.cr.commit()
            raise UserError(str(e))

    @http.route(
        "/net_dragon/check",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def net_dragon_check_code(self, **kw):
        validate = BaseController.get_validated(kw, {
            "code": "string|required",
            "signature": "string|required",
            "nonce": "string|required",
            "email": "string|required",
            "user_id": "string|required",
            "sp_hash": "string|required",
            "product_id": "number|required"
        })
        self.check_redemption_portal_signature(validate)
        if not validate.get('sp_hash') or not isinstance(validate.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validate.get('sp_hash'))])
        if not user:
            raise AccessDenied()
        param = {"codes": [{"code": validate["code"]}]}
        product_id = request.env["product.template"].sudo().search([('id', '=', validate.get('product_id'))])
        if product_id.service_provider_id.id != user.id:
            raise AccessDenied()
        param["sku"] = product_id.SKU
        check_res = RedeemController.check_code_with_hash_func(user=user, param=param)
        return BaseController._create_response(data=check_res["data"][0], message="Checked Successfully")

    @http.route(
        "/net_dragon/redeem",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def net_dragon_charge_balance(self, **kw):
        validate = BaseController.get_validated(kw, {
            "code": "string|required",
            "user_id": "string|required",
            "email": "string|required",
            "zone_id": "string",
            "signature": "string|required",
            "nonce": "string|required",
            "sp_hash": "string|required",
            "product_id": "number|required"
        })
        if not validate.get('sp_hash') or not isinstance(validate.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validate.get('sp_hash'))])
        if not user:
            raise AccessDenied()

        # check code
        param = {"codes": [{"code": validate["code"]}]}
        user_id = validate.get("user_id")
        zone_id = validate.get("zone_id") if validate.get("zone_id") else "101"

        service_provider_id = user.netdragon_account_name
        service_provider_secret = user.netdragon_account_secret
        self.check_redemption_portal_signature(validate)

        product_id = request.env["product.template"].sudo().search([('id', '=', validate.get('product_id'))])
        if product_id.service_provider_id.id != user.id:
            raise AccessDenied()
        param["sku"] = product_id.SKU

        check_res = RedeemController.check_code_with_hash_func(user=user, param=param)
        if check_res['code'] != 200:
            raise UserError(check_res["message"])
        if check_res["data"][0].get("product_specific_attribute") != 'topup':
            raise UserError("Invalid Code")
        if check_res["data"][0].get("found") != True or check_res["data"][0]["expired"] != False:
            raise UserError("Code Not Found Or Expired")
        args = kw.copy()
        args["product_type"] = "serial"
        args['user_id'] = args['email']
        redeem_res = RedeemController.redeem_func(args, user)

        if redeem_res['code'] != 200:
            raise UserError(redeem_res["message"])

        if redeem_res["data"].get("is_redeemed") != '3':
            raise UserError("Code Already Used")
        log = {
            'code': validate["code"],
        }
        taxId = str(randint(100000, 999999999999999))
        # validation_request, validation_response =\
        #     self.call_net_dragon_validate(service_provider_id, user_id, zone_id, check_res["data"][0]["product_currency"],
        #                                   check_res["data"][0]["product_amount"], check_res["data"][0]["sku"], taxId,
        #                                   service_provider_secret
        #                                   )
        try:
            # log["validate_request_body"] = validation_request
            # log["validate_response_result"] = validation_response
            # if validation_response and validation_response.get("error"):
            #     request.env.cr.rollback()
            #     request.env['netdragon.log'].sudo().create(log)
            #     return BaseController._create_response(data={}, message=validation_response.get("error")["message"])

            topup_request_body, topup_response_body = self.call_net_dragon_topup(service_provider_id, user_id,
                                                                                 zone_id, check_res["data"][0][
                                                                                     "product_currency"],
                                                                                 check_res["data"][0]["product_amount"],
                                                                                 product_id, taxId,
                                                                                 service_provider_secret
                                                                                 )
            log["topup_request_body"] = topup_request_body
            log["topup_response_body"] = topup_response_body
            if topup_response_body.get("error"):
                request.env.cr.rollback()
                request.env['netdragon.log'].sudo().create(log)
                return BaseController._create_response(data={}, message=topup_response_body.get("error")["message"])
            log["our_message"] = check_res["data"][0]
            request.env['netdragon.log'].sudo().create(log)
            template = self.env.ref('redeemly_pin_management.successful_topup_operation_template')
            if product_id and args['email']:
                email_values = {
                    'email_from': 'noreply@skarla.com',
                    'email_to': args['email']
                }
                template.with_context().send_mail(product_id.id, email_values=email_values)
            return BaseController._create_response(data=check_res["data"][0],
                                                   message="Your Account topup operation done successfully")
        except Exception as e:
            request.env.cr.rollback()
            request.env['netdragon.log'].sudo().create(log)
            return BaseController._create_response(data={}, message=str(e))

    @staticmethod
    def check_redemption_portal_signature(param):
        message = param.get("code") + param.get("nonce") + param.get("user_id") + param.get("email") + \
                  str(param.get('product_id'))
        secret = config.get('net_dragon_redemption_portal_secret')
        temp = hmac.new(
            bytes(secret, 'latin-1'),
            msg=bytes(message, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        if temp != param.get("signature"):
            raise UserError("Invalid Request")

    @staticmethod
    def check_redemption_portal_signature(param):
        message = param.get("code") + param.get("nonce") + param.get("user_id") + param.get("email")
        secret = config.get('net_dragon_redemption_portal_secret')
        temp = hmac.new(
            bytes(secret, 'latin-1'),
            msg=bytes(message, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        if temp != param.get("signature"):
            raise UserError("Invalid Request")

    @staticmethod
    def call_net_dragon_validate(service_provider, user_id, zone_id,
                                 price_currency, price_amount, product, txn_id,
                                 service_provider_key, quantity=1, payment_channel=0):
        if not product.netdragon_product_category or not product.netdragon_product_category.sku \
                or not product.netdragon_product_category.endpoint:
            raise UserError("Product Category Not Defined")

        endpoint = config.get("net_dragon_base_url") + product.netdragon_product_category.endpoint
        is_for_test = int(config.get("net_dragon_is_for_test"))
        body = {
            "id": txn_id,
            "jsonrpc": "2.0",
            "method": "validate",
            "param": [{
                "serviceProvider": service_provider,
                "isForTest": is_for_test,
                "signature": "",
                "user": {"userId": user_id, "zoneId": zone_id},
                "price": {"currency": price_currency, "amount": str(price_amount)},
                "sku": product.netdragon_product_category.sku,
                "quantity": quantity,
                "paymentChannelId": payment_channel,
                "txnId": txn_id
            }]
        }
        body["param"][0]["signature"] = NetDragonController. \
            generate_net_dragon_signature(body=body, service_provider_secret=service_provider_key)
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(body)
        response = requests.request(
            "POST", endpoint + "/validate", headers=headers, data=payload)
        res = json.loads(response.text)

        return body, res

    @staticmethod
    def call_net_dragon_topup(service_provider, user_id, zone_id,
                              price_currency, price_amount, product, txn_id,
                              service_provider_key, quantity=1, payment_channel=0):
        if not product.netdragon_product_category or not product.netdragon_product_category.sku \
                or not product.netdragon_product_category.endpoint:
            raise UserError("Product Category Not Defined")
        endpoint = config.get("net_dragon_base_url") + product.netdragon_product_category.endpoint
        is_for_test = int(config.get("net_dragon_is_for_test"))
        body = {
            "id": txn_id,
            "jsonrpc": "2.0",
            "method": "topup",
            "param": [{
                "serviceProvider": service_provider,
                "isForTest": is_for_test,
                "user": {"userId": user_id, "zoneId": zone_id},
                "price": {"currency": price_currency, "amount": str(price_amount)},
                "sku": product.netdragon_product_category.sku,
                "quantity": quantity,
                "paymentChannelId": payment_channel,
                "txnId": txn_id
            }]
        }
        body["param"][0]["signature"] = NetDragonController. \
            generate_net_dragon_signature(body=body, service_provider_secret=service_provider_key)
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(body)
        response = requests.request(
            "POST", endpoint + "/topup", headers=headers, data=payload)
        res = json.loads(response.text)
        return body, res

    @staticmethod
    def generate_net_dragon_signature(body, service_provider_secret):
        message = body["id"] + body["jsonrpc"] + body["method"] + body["param"][0]["serviceProvider"] + \
                  body["param"][0]["txnId"] + body["param"][0]["user"]["userId"] + body["param"][0]["user"]["zoneId"] + \
                  body["param"][0]["price"]["currency"] + \
                  body["param"][0]["price"]["amount"] + body["param"][0]["sku"] + str(body["param"][0]["quantity"]) + \
                  str(body["param"][0]["paymentChannelId"]) + str(body["param"][0]["isForTest"])

        signature = hmac.new(
            bytes(service_provider_secret, 'latin-1'),
            msg=bytes(message, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature

    @http.route(
        "/net_dragon/get_image_slider",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def net_dragon_get_image_slider(self, **kw):
        validate = BaseController.get_validated(kw, {
            "sp_hash": "string|required",
        })
        if not validate.get('sp_hash') or not isinstance(validate.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validate.get('sp_hash'))])
        if not user:
            raise AccessDenied()
        sliders = request.env['netdragon.slider'].sudo().search([])
        return BaseController._create_response(
            {'data': [item.serialize_for_api() for item in sliders], 'totalCount': len(sliders)})

    @http.route(
        "/net_dragon/get_product_category",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def net_dragon_get_product_category(self, **kw):
        validate = BaseController.get_validated(kw, {
            "sp_hash": "string|required",
            "category_id": "number"
        })
        if not validate.get('sp_hash') or not isinstance(validate.get('sp_hash'), str):
            raise AccessDenied()
        user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validate.get('sp_hash'))])
        if not user:
            raise AccessDenied()
        category_id = validate.get("category_id")
        domain = []
        if category_id:
            domain.append(('id', '=', category_id))
        categories = request.env['netdragon.product.category'].sudo().search(domain)
        return BaseController._create_response(
            {'data': [item.serialize_for_api() for item in categories], 'totalCount': len(categories)})

    # @http.route(
    #     "/net_dragon/contact_us",
    #     type="json",
    #     auth="none",
    #     save_session=False,
    #     cors=config.get("control_panel_url"),
    #     csrf=False
    # )
    # @BaseController.with_errors
    # def net_dragon_contact_us(self, **kw):
    #     validate = BaseController.get_validated(kw, {
    #         "name": "string",
    #         "email": "string",
    #         "mobile": "string",
    #         "country": "string",
    #         "subject": "string",
    #         "message": "string"
    #     })
    #     template = self.env.ref("redeemly_pin_management.contact_us_email_template")
    #     email_values = {
    #         'email_from': 'noreply@skarla.com'
    #     }
    #     logo_url = self.env['res.partner'].sudo().search([('id', '=', self.env.company.partner_id.id)]).partner_logo_url
    #     context = {}
    #     template.with_context(context).send_mail(self.id, email_values=email_values)
