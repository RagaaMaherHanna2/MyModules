import logging
from datetime import datetime, timedelta
from odoo import http, SUPERUSER_ID , _
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.addons.redeemly_pin_management.controllers.pull_controller import PullController
from odoo.addons.redeemly_pin_management.controllers.redeem_controller import RedeemController
from odoo.http import request
import jwt
import time
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied
from hashlib import sha256
from odoo.addons.auth_totp.models.totp import TOTP, TOTP_SECRET_SIZE
from odoo.addons.auth_totp.models.totp import ALGORITHM, DIGITS, TIMESTEP
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.http import request
from random import random

import base64
import os
import re
import io
import qrcode
import json
import requests

import werkzeug.urls
import functools
import string


compress = functools.partial(re.sub, r'\s', '')


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

_logger = logging.getLogger(__name__)
FOODIC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class FoodicsController(BaseController):

    @http.route(
        "/foodics/authenticate",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def foodics_authenticate(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "login": "required|string",
                "password": "required|string",
            },
        )
        uid = request.session.authenticate(
            config.get("db_name"), validated["login"], validated["password"]
        )
        user = request.env(user=uid)['res.users'].browse(uid)
        if uid:
            validator = request.env.ref("redeemly_pin_management.redeemly_token_validator").with_user(
                SUPERUSER_ID
            )
            exp = time.time() + 1 * 60 * 60
            payload = dict(
                aud=validator.audience,
                iss=validator.issuer,
                exp=time.time() + 1 * 60 * 60,
            )
            payload["uid"] = uid

            payload["email"] = validated["login"]
            token = jwt.encode(
                payload, key=validator.secret_key, algorithm=validator.secret_algorithm
            )

            return BaseController._create_response(
                {"is_2factor": False, "token": token})
        else:
            return BaseController._create_response("", 403, "Access Denied")

    @http.route(
        "/foodics/pull_codes",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_http_errors
    def pull_codes_foodics(self, **kwargs):
        try:
            kw = json.loads(request.httprequest.get_data().decode(request.httprequest.charset))
            user = BaseController.key_authenticate(kw)
            validated = BaseController.get_validated(kw["params"], {
                "product": "number|required",
                "customer_mobile_number": "string|required",
                "mobile_country_code": "string|required",
                "business_reference": "string|required",
                "customer_name": "string",
                "quantity": "number",
                "user_id": "string",
                "email_id": "string",
            })
            res = PullController.pull_codes(validated, user)
            return BaseController._create_foodic_response(res, 200, "")
        except Exception as e:
            return BaseController._create_foodic_response({}, 400, str(e))

    @http.route(
        "/foodics/reward",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False,
    )
    @BaseController.with_http_errors
    def reward_foodics(self, **kwargs):
        try:
            kw = json.loads(request.httprequest.get_data().decode(request.httprequest.charset))
            user = BaseController.foodic_key_authenticate(kw)
            validated = BaseController.get_validated(kw, {
                  "business_reference": "string",
                  "customer_mobile_number": "string",
                  "mobile_country_code": "string",
                  "reward_code": "string"
            })
            if not (user.is_service_provider or user.is_merchant):
                raise BaseController._create_foodic_response({}, 400, "Auth Failed")

            validated_serial = validated['reward_code']
            customer_mobile_number = validated['customer_mobile_number']
            mobile_country_code = validated['mobile_country_code']
            serial = request.env['product.serials'].with_user(1).search(
                [('serial_code_hash', '=', sha256(validated_serial.encode('utf-8')).hexdigest()),
                 ('customer_mobile_number', '=', customer_mobile_number),
                 ('mobile_country_code', '=', mobile_country_code)
                 ])

            if (not serial) or (user.is_service_provider and serial.product_id.service_provider_id.id != user.id):
                return BaseController._create_foodic_response({}, 400, "Not Found")
            if (serial.expiry_date and serial.expiry_date < datetime.now().date()) or serial.state == '4':
                return BaseController._create_foodic_response({}, 400, "Not Found")
            serial.check_count = serial.check_count + 1
            reward_result = {
                "type": int(serial.product_id.foodics_discount_type),
                "discount_amount": serial.product_id.foodics_discount_amount,
                "is_percent": serial.product_id.foodics_is_percent,
                "customer_mobile_number": serial.customer_mobile_number,
                "mobile_country_code": serial.mobile_country_code,
                "business_reference": serial.product_id.foodics_business_reference,
                "max_discount_amount": serial.product_id.foodics_max_discount_amount,
                "discount_includes_modifiers": serial.product_id.foodics_include_modifiers,
                "allowed_products": [{
                            "products_list": [item.product_id for item in serial.product_id.foodics_allowed_products]
                        }]
                    if serial.product_id.foodics_allowed_products else None,
                "is_discount_taxable": serial.product_id.foodics_is_discount_taxable
            }

            serial.last_check_time = datetime.now()
            return BaseController._create_foodic_response(reward_result, 200, "")
        except Exception as e:
            return BaseController._create_foodic_response({}, 400, str(e))

    @http.route(
        "/foodics/redeem",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_http_errors
    def redeem_foodics(self, **kwargs):
        try:
            kw = json.loads(request.httprequest.get_data().decode(request.httprequest.charset))
            user = BaseController.foodic_key_authenticate(kw)
            validated = BaseController.get_validated(kw, {
                "branch_id": "string",
                "business_reference": "string",
                "discount_amount": "number",
                "mobile_country_code": "string",
                "customer_mobile_number": "string",
                "date": "string",
                "user_id": "string",
                "order_id": "string",
                "reward_code": "string",
            })
            if not user.is_service_provider:
                return BaseController._create_foodic_response({}, 400, "")

            validated['code'] = validated['reward_code']
            validated['product_type'] = 'serial'
            response = RedeemController.redeem_func(validated, user)
            return response
        except Exception as e:
            return BaseController._create_foodic_response({}, 400, str(e))

    @http.route(
        '/exposed/foodics/foodics-new',
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    def web_foodics_install(self, redirect=None, **kw):
        user = self.get_user(request.uid)
        if not user:
            raise UserError("Invalid User")

        validated = BaseController.get_validated(kw, {
            "code": "string",
            "state": "string",
        })

        if not user.is_foodics_cashier:
            raise UserError("Invalid User")
        print("########## ROUTe #####")
        print(http.request)
        # code = http.request.params.get('code')
        # state = http.request.params.get('state')
        code = validated['code']
        state = validated['state']


        if user.foodics_random_state != state:
            raise UserError("Invalid Data")

        if user and request.httprequest.method == 'POST':
            try:
                with user._assert_can_auth():
                    validation_request, validation_response = \
                        self.call_foodics_bearar_token(code, state,
                                                       config.get("client_id"),
                                                       config.get("client_secret")
                                                       )
                    try:
                        if validation_response and validation_response.get("error"):
                            raise UserError("User Not Found")

                        access_token = validation_response.get("result")["access_token"]
                        user.foodics_bearar_token = access_token
                        return BaseController._create_response(data={}, message="Successfully")

                    except Exception as e:
                        raise UserError(str(e))
            except AccessDenied as e:
                error = str(e)
            except ValueError:
                return BaseController._create_response("", 403, "Invalid authentication code format.")

    @http.route(
        '/exposed/foodics/preinstall',
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    def web_foodics_pre_install(self):
        user = self.get_user(request.uid)

        if not user:
            raise UserError("Invalid User")

        if not user.is_foodics_cashier:
            raise UserError("Invalid User")

        if user and request.httprequest.method == 'POST':
            try:
                client_id = config.get("client_id")
                random_byte = os.urandom(16)
                random_string = base64.b64encode(random_byte, altchars=b'+/').decode('utf-8')[:16]
                user.sudo().foodics_random_state = random_string  # "redeemly"
                return BaseController._create_response(
                    data=
                    {
                        'redirect_url': f"https://console-sandbox.foodics.com/authorize?client_id={client_id}&state={user.sudo().foodics_random_state}"},
                    message="Successfully")
            except AccessDenied as e:
                error = str(e)
            except ValueError:
                return BaseController._create_response("", 403, "Invalid authentication code format.")

    @staticmethod
    def call_foodics_bearar_token(code, client_id, client_secret, state):
        state = ""

        # endpoint = config.get("foodics_base_url") + NETDRAGON_API[sku]
        endpoint = "https://api-sandbox.foodics.com/oauth/token"
        body = {
            "jsonrpc": "2.0",
            "param": [{
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "https://www.myApp.com/foodics-success"
            }]
        }
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(body)
        response = requests.request(
            "POST", endpoint, headers=headers, data=payload)
        res = json.loads(response.text)

        return body, res