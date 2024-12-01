import logging
from datetime import datetime, timedelta
from odoo import http, SUPERUSER_ID , _
from odoo.http import request
import jwt
import time
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied

from odoo.addons.auth_totp.models.totp import TOTP, TOTP_SECRET_SIZE
from odoo.addons.auth_totp.models.totp import ALGORITHM, DIGITS, TIMESTEP
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


import base64
import os
import re
import io
import qrcode


import werkzeug.urls
import functools


compress = functools.partial(re.sub, r'\s', '')


_logger = logging.getLogger(__name__)


class RedeemlyAuthentication(BaseController):
    @http.route(
        "/exposed/auth/whoami",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def whoami(self):
        data = {}
        if request.jwt_partner_id:
            user = self.get_user(request.uid).sudo()
            currency_symbol = '$'
            if user.is_service_provider:
                currency_symbol = user.sudo().sp_currency.symbol
            elif user.is_merchant:
                if user.create_uid.is_service_provider:
                    currency_symbol = user.sudo().create_uid.sp_currency.symbol
            if user.is_sub_merchant:
                if user.parent_merchant.create_uid.is_service_provider:
                    currency_symbol = user.sudo().parent_merchant.create_uid.sp_currency.symbol


            data.update(
                name=user.name, email=user.email, reference=user.reference,
                redeemly_api_key=user.redeemly_api_key,
                roles=user.get_user_roles(),
                sp_hash=user.sp_hash if user.is_service_provider else False,
                totp_enabled=user.totp_enabled,
                permissions=user.sudo().get_permissions(),
                currency_symbol=currency_symbol,
                codes_additional_value=user.codes_additional_value if user.is_service_provider else False,
                default_categ_id=user.default_categ_id.id if user.is_service_provider else False,
                default_categ_name=user.default_categ_id.name if user.is_service_provider else False

            )
        return BaseController._create_response(data)

    @http.route(
        "/exposed/auth/refresh_api_key",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def refresh_api_key(self):
        user = self.get_user(request.uid)
        key = user.regenerate_api_key()
        return BaseController._create_response({"redeemly_api_key": key})

    @http.route(
        "/exposed/auth/authenticate",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def authenticate(self, **kw):
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
        if not user.totp_enabled:
            if uid:
                validator = request.env.ref("redeemly_pin_management.redeemly_token_validator").with_user(
                    SUPERUSER_ID
                )
                exp = time.time() + 24 * 60 * 60
                payload = dict(
                    aud=validator.audience,
                    iss=validator.issuer,
                    exp=time.time() + 24 * 60 * 60,
                )
                payload["uid"] = uid

                payload["email"] = validated["login"]
                token = jwt.encode(
                    payload, key=validator.secret_key, algorithm=validator.secret_algorithm
                )

                return BaseController._create_response(
                    {"is_2factor": False, "token": token, "first_login": request.env.user.first_login,
                     "new_token": True})
            else:
                return BaseController._create_response("", 403, "Access Denied")
        else:
            user.sudo().set_last_session_id_2_factor()
            return BaseController._create_response(
                {"is_2factor": True, 'first_login': user.first_login, "message": "Please verify code ", "key": user.sudo().last_session_id_2_factor}
            )

    @http.route(
        '/exposed/login/totp',
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    def web_totp_api(self, redirect=None, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "totp_token": "required|string",
                "login": "required|string",
                "key": "required|string",
            },
        )

        user = request.env['res.users'].with_user(SUPERUSER_ID).search(
            [('email', '=ilike', validated['login']), ('last_session_id_2_factor', '=', validated['key']),
             ('last_session_id_2_factor_time', '>=', datetime.now() - timedelta(hours=1))])
        if not user:
            raise UserError("Invalid Email or totp token or key")
        uid = user.id

        user = request.env(user=uid)['res.users'].browse(uid)

        if user and request.httprequest.method == 'POST' and validated["totp_token"]:
            try:
                with user._assert_can_auth():

                    if (user._totp_check_api(int(re.sub(r'\s', '', validated["totp_token"])))):
                        if uid:
                            validator = request.env.ref("redeemly_pin_management.redeemly_token_validator").with_user(
                                SUPERUSER_ID
                            )
                            exp = time.time() + 24 * 60 * 60
                            payload = dict(
                                aud=validator.audience,
                                iss=validator.issuer,
                                exp=time.time() + 24 * 60 * 60,
                            )
                            payload["uid"] = uid
                            payload["email"] = validated["login"]
                            token = jwt.encode(
                                payload, key=validator.secret_key, algorithm=validator.secret_algorithm
                            )

                            # _token = request.env["api.access_token"]
                            # access_token = _token.find_one_or_create_token(user_id=uid, token=token, exp=exp,
                            #                                                create=True)
                            user.sudo().last_session_id_2_factor = None
                            user.sudo().last_session_id_2_factor_time = None
                            return BaseController._create_response(
                                {"is_2factor": True, "token": token, "first_login": request.env.user.first_login,
                                 "new_token": True})
                        else:
                            return BaseController._create_response("", 403, "Access Denied")
                    else:
                        return BaseController._create_response("", 403,
                                                               "Verification failed, please double-check the 6-digit code.")
            except AccessDenied as e:
                error = str(e)
            except ValueError:
                return BaseController._create_response("", 403, "Invalid authentication code format.")

    @http.route(
        "/exposed/auth/create_merchant_account",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_merchant_account(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "name": "string|required",
                "email": "string|required",
                "password": "string|required"
            },
        )
        user = request.env.user
        if user.is_service_provider:
            partner = (
                request.env["res.partner"]
                    .sudo()
                    .create(
                    {
                        "name": validated["name"],
                        "email": validated["email"]
                    }
                )
            )
            user = (
                request.env["res.users"]
                    .sudo()
                    .with_context(no_reset_password=True)
                    .create(
                    {
                        "login": validated["email"],
                        "password": validated["password"],
                        "groups_id": [request.env.ref("base.group_portal").id],
                        "is_merchant": True,
                        "company_id": 1,
                        "partner_id": partner.id,
                        "first_login": True
                    }
                )
            )
            partner.user_id = user.id
            validated["id"] = user.id
            return BaseController._create_response(validated)
        else:
            return BaseController._create_response(validated, 403, "Access Denied")

    @http.route(
        "/exposed/auth/change_password",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def change_password(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "old_password": "string|required",
                "new_password": "string|required"
            },
        )
        request.env.user.sudo().change_password(validated["old_password"], validated["new_password"])
        request.env.user.first_login = False
        return BaseController._create_response("ok", message='Password Changed successfully')

    @http.route(
        "/exposed/auth/reset_password",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def reset_password(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "email": "string|required",
                "url": "string"
            },
        )
        user = request.env['res.users'].with_user(SUPERUSER_ID).search([('email', '=ilike', validated['email'])])
        if not user:
            raise UserError("Invalid Email")
        user.change_password_and_send_email(validated['url'])
        return BaseController._create_response("ok", message='Password reset successfully, please check your email')

    @http.route(
        "/exposed/auth/reset_password_confirmed",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def reset_password_confirmed(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "token": "string|required",
                "new_password": "string|required"
            },
        )
        user = request.env['res.users'].with_user(SUPERUSER_ID).search([('token_random', '=', validated['token']),
                                                                        ('key_creation_time', '>=', datetime.now() - timedelta(hours=1))
                                                                        ])
        if not user:
            raise UserError("Invalid Request")
        user.password = validated['new_password']
        user.key_creation_time = False
        user.token_random = False
        return BaseController._create_response("ok", message='Password Changed Successfully, please re-login')

    @http.route(
        "/exposed/auth/get_new_merchants",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_new_merchants(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "offset": "number",
                "limit": "number",
                "id": "number",
                "name": "string"
            },
        )
        user = request.env.user
        if not user.is_service_provider:
            raise AccessDenied()
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0

        domain = ['|','&',('create_uid', '=', user.id),
                  ('is_merchant', '=', True),
                  ('invites_ids.product.service_provider_id', '=', user.id)
                  ]

        if validated.get("id"):
            domain.append(('id', '=', validated.get('id')))
        if validated.get('name'):
            domain.append(('name', 'ilike', validated.get('name')))

        data = request.env['res.users'].sudo().search(domain, limit=limit, offset=offset)
        count = request.env['res.users'].sudo().search_count(domain)
        result = [item.serialize_for_api(validated["id"]) for item in data]
        return BaseController._create_response({"data": result, "totalCount": count}, message='')

    @http.route(
        "/exposed/login/enable2f",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def login_enable_2f_authentication(self, **kw):
        user = request.env.user

        if user.sudo().totp_enabled:
            raise UserError(_("Two-factor authentication already enabled"))

        secret_bytes_count = TOTP_SECRET_SIZE // 8
        secret = base64.b32encode(os.urandom(secret_bytes_count)).decode()
        # format secret in groups of 4 characters for readability
        secret = ' '.join(map(''.join, zip(*[iter(secret)] * 4)))

        global_issuer = request and request.httprequest.host.split(':', 1)[0]

        issuer = global_issuer or user.company_id.display_name
        url = werkzeug.urls.url_unparse((
            'otpauth', 'totp',
            werkzeug.urls.url_quote(f'{issuer}:{user.login}', safe=':'),
            werkzeug.urls.url_encode({
                'secret': compress(secret),
                'issuer': issuer,
                # apparently a lowercase hash name is anathema to google
                # authenticator (error) and passlib (no token)
                'algorithm': ALGORITHM.upper(),
                'digits': DIGITS,
                'period': TIMESTEP,
            }), ''
        ))

        data = io.BytesIO()
        qrcode.make(url.encode(), box_size=4).save(data, optimise=True, format='PNG')
        w_qrcode = base64.b64encode(data.getvalue()).decode()
        return BaseController._create_response({"qrcode": w_qrcode, "secret": secret})

    @http.route(
        "/exposed/login/active_enable2f",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def active_login_enable_2f_authentication(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "code": "string|required",
                "secret": "string|required",
            },
        )
        user = request.env.user
        try:
            c = int(compress(validated["code"]))
        except ValueError:
            raise UserError(_("The verification code should only contain numbers"))

        if user._totp_try_setting_api(validated["secret"], c):
            user.sudo().totp_secret = compress(validated["secret"]).upper()
            user.sudo().totp_enabled = True

            return BaseController._create_response("ok", message='Verification Code  successfully')
        raise UserError(_('Verification failed, please double-check the 6-digit code'))

    @http.route(
        "/exposed/2f/disable",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def disable_2f_authentication(self, **kw):
        user = request.env.user
        user.revoke_all_devices()
        user.sudo().write({'totp_secret': False})

        return BaseController._create_response("ok", message='Two-factor authentication disabled')

    @http.route(
        "/exposed/logout",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def logout_authentication(self, **kw):
        user = self.get_user(request.uid)
        request.session.logout()

        return BaseController._create_response("ok", message='Logout authentication Successfully')

    # send six digit by email of users
    @http.route(
        "/exposed/login/refresh2f",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def refresh_2f_authentication(self, **kw):
        user = request.env.user
        validated = BaseController.get_validated(
            kw,
            {
                "refresh_route": "string"
            },
        )
        if not user.sudo().totp_enabled:
            raise UserError(_("Two-factor authentication already NOT enabled"))
        user.sudo().send_email_verify_2_factor(validated["refresh_route"])
        return BaseController._create_response("ok", message='Six Digits Send  , please check your email')

    # active six digit send by email and send  Qr code
    @http.route(
        "/exposed/login/activ_refresh2f",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def active_refresh_2f_authentication(self, **kw):

        validated = BaseController.get_validated(
            kw,
            {
                "code": "string|required",
            },
        )

        user = request.env.user

        if not user.sudo().totp_enabled:
            raise UserError(_("Two-factor authentication already NOT enabled"))

        if  (user.sudo().last_six_digit_for_2f_reation_time >= datetime.now() - timedelta(
                hours=1)) and user.sudo().last_six_digit_for_2f == validated["code"]:
            # 1-user.revoke_all_devices()
            secret_bytes_count = TOTP_SECRET_SIZE // 8
            secret = base64.b32encode(os.urandom(secret_bytes_count)).decode()
            # format secret in groups of 4 characters for readability
            secret = ' '.join(map(''.join, zip(*[iter(secret)] * 4)))

            global_issuer = request and request.httprequest.host.split(':', 1)[0]

            issuer = global_issuer or user.company_id.display_name
            url = werkzeug.urls.url_unparse((
                'otpauth', 'totp',
                werkzeug.urls.url_quote(f'{issuer}:{user.login}', safe=':'),
                werkzeug.urls.url_encode({
                    'secret': compress(secret),
                    'issuer': issuer,
                    # apparently a lowercase hash name is anathema to google
                    # authenticator (error) and passlib (no token)
                    'algorithm': ALGORITHM.upper(),
                    'digits': DIGITS,
                    'period': TIMESTEP,
                }), ''
            ))

            data = io.BytesIO()
            qrcode.make(url.encode(), box_size=4).save(data, optimise=True, format='PNG')
            w_qrcode = base64.b64encode(data.getvalue()).decode()
            # 2-user.sudo().totp_secret = compress(secret).upper()
            return BaseController._create_response({"qrcode": w_qrcode, "secret": secret})
        else:
            raise UserError(_("Six Digits Code or Old Code Not Correct Please Check Or Six Digit Code Expired Time"))

    # activate new qr code submitted by user with insert  code after scan
    @http.route(
        "/exposed/login/activ_refresh2f_qr_code",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def active_refresh_2f_qr_code(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "code": "string|required",
                "secret": "string|required",
            },
        )
        user = request.env.user
        try:
            c = int(compress(validated["code"]))
        except ValueError:
            raise UserError(_("The verification code should only contain numbers"))

        if user._totp_try_setting_api_refresh(validated["secret"], c):
            if (user.sudo().last_six_digit_for_2f_reation_time >= datetime.now() - timedelta(
                    hours=1)):
                user.revoke_all_devices()
                user.sudo().totp_secret = compress(validated["secret"]).upper()

                return BaseController._create_response("ok", message='Refresh QR Code  successfully')
            else:
                raise UserError(_("Six Digit Code Expired Time , Please Follow Cycle Of Refresh Code From scratch"))
        raise UserError(_('Verification failed, please double-check the 6-digit code'))

    @http.route('/exposed/check_api', type="http",
                auth="none",
                save_session=False,
                cors=config.get("control_panel_url"),
                csrf=False)
    def check_api(self, **kwargs):
        return "true"