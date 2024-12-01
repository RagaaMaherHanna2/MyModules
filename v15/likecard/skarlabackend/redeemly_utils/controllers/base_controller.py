import base64
import functools
import json
from odoo.exceptions import UserError

from werkzeug.exceptions import Unauthorized

from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessDenied
from odoo.tools.config import config
import re
from werkzeug.exceptions import Forbidden

Sub_Routes = ['/exposed/', '/babil_game/', '/net_dragon/', ]


class UnauthorizedInsufficientPermission(AccessDenied):
    pass


# class SkarlaRoot(http.Root):
#     def get_request(self, httprequest):
#         if config.get('disable_integration') and any(route in httprequest.url for route in Sub_Routes):
#             raise Forbidden("Sorry, Server Is In Maintenance")
#
#         # Call the parent dispatch() method to handle the request
#         return super(SkarlaRoot, self).get_request(httprequest)
# #
# # http.Root = SkarlaRoot
# http.root = SkarlaRoot()

class BaseController(http.Controller):

    @staticmethod
    def _create_response(data, status=200, message=""):
        result = {
            "message": message,
            "data": data,
            'code': status,
        }
        request._json_response = BaseController.alternative_json_response

        return result

    @staticmethod
    def _create_foodic_response(data, status=200, message=""):
        result = {
            "message": message,
            "data": data,
            'code': status,
        }
        request._json_response = BaseController.alternative_foodics_json_response

        return result

    @staticmethod
    def alternative_json_response(result=None, error=None):
        body = {
            "ok": True,
            "message": "",
            "result": {}
        }
        if result is not None:
            if result.get("code"):
                body['ok'] = 200 >= result['code'] < 400
            if result.get("message"):
                body['message'] = result['message']
            if result.get("data"):
                body['result'] = result['data']

            body = json.dumps(body)

        elif error is not None:
            body = {"ok": False, 'message': error['data']['message']}
            if error.get("data"):
                body['result'] = error['data']
            body = json.dumps(body)

        status = 400
        if error and error['data'] and error['data'][
            'name'] == 'odoo.addons.auth_jwt.exceptions.UnauthorizedInvalidToken':
            status = 401

        return Response(
            body, status=status if error else 200,
            headers=[('Content-Type', "application/json"),
                     ('Content-Length', len(body)),
                     ('Access-Control-Allow-Origin', config.get('control_panel_url'))
                     ]
        )

    @staticmethod
    def alternative_foodics_json_response(result=None, error=None):
        body = {
        }
        status = 200
        if result is not None:
            status = result.get('code') if result.get('code') else 200
            if result.get("data"):
                body = result['data']

            body = json.dumps(body)

        elif error is not None:
            status = 400
            body = {'message': error['data']['message']}
            if error.get("data"):
                body['result'] = error['data']
            body = json.dumps(body)

        if error and error['data'] and error['data'][
            'name'] == 'odoo.addons.auth_jwt.exceptions.UnauthorizedInvalidToken':
            status = 401
            body = json.dumps(body)

        return Response(
            body, status=status,
            headers=[('Content-Type', "application/json"),
                     ('Content-Length', len(body)),
                     ('Access-Control-Allow-Origin', config.get('control_panel_url'))
                     ]
        )

    @staticmethod
    def get_partner(jwt_partner_id):
        return request.env["res.partner"].browse(jwt_partner_id)

    @staticmethod
    def get_user(jwt_user_id):
        return request.env["res.users"].browse(jwt_user_id)

    @staticmethod
    def get_user_by__website_api_key(api_key):
        return request.env['website.api.key'].sudo().search([]).filtered(
            lambda k: k.website_redeemly_api_key == api_key).user_id or request.env["res.users"].sudo().search(
            [('redeemly_api_key', '=', api_key)])

    @staticmethod
    def get_user_by_api_key(api_key):
        return request.env["res.users"].sudo().search([('redeemly_api_key', '=', api_key)])

    @staticmethod
    def get_validated(kw, validation_rules, req_only=False):
        validated = {}
        lang = kw.get('language')
        if not lang:
            lang = 'en'
        if lang == 'ar':
            lang = 'ar_001'
        request.session['context']['lang'] = lang
        request.session['from_json_code'] = True
        for field, rules in validation_rules.items():
            for rule in rules.split("|"):
                if kw.get(field) is None:
                    if rule == 'required':
                        raise ValidationError(f"{field} is missing")
                    continue
                if rule == 'list' and not isinstance(kw.get(field), list):
                    raise ValidationError(f'{field} must be a list')
                if rule == 'dict' and not isinstance(kw.get(field), dict):
                    raise ValidationError(f'{field} must be an object')
                if rule == 'number' and not isinstance(kw.get(field), int) and not isinstance(kw.get(field), float):
                    raise ValidationError(f'{field} must be a number')
                elif rule == 'int' and not isinstance(kw.get(field), int):
                    raise ValidationError(f'{field} must be a integer')
                elif rule == 'float' and not isinstance(kw.get(field), float):
                    raise ValidationError(f'{field} must be a floating point number')
                elif rule == 'boolean' and not isinstance(kw.get(field), bool):
                    raise ValidationError(f'{field} must be a boolean')
                elif rule == 'string' and not isinstance(kw.get(field), str):
                    raise ValidationError(f'{field} must be a string')
                elif rule == 'url' and (
                        not isinstance(kw.get(field), str) or not BaseController.is_valid_url(kw.get(field))):
                    raise ValidationError(f'{field} must be a url')
                elif rule == 'image' and (not isinstance(kw.get(field), str) or (
                        not BaseController.is_valid_url(kw.get(field)) and not BaseController.is_valid_base64_image(
                    kw.get(field)))):
                    raise ValidationError(f'{field} must be a url or base64')
            if not req_only:
                validated[field] = kw.get(field)
            elif kw.get(field) is not None:
                validated[field] = kw.get(field)
        return validated

    @staticmethod
    def with_errors(func):
        @functools.wraps(func)
        def inner(*k, **kw):
            try:
                return func(*k, **kw)
            except UnauthorizedInsufficientPermission as e:
                request.env.cr.rollback()
                raise AccessDenied("100 Insufficient Privileges")
            except Exception as ex:
                request.env.cr.rollback()
                return BaseController._create_response({}, 400, str(ex))

        return inner

    @staticmethod
    def with_http_errors(func):
        @functools.wraps(func)
        def inner(*k, **kw):
            try:
                return func(*k, **kw)
            except Exception as ex:
                request.env.cr.rollback()
                return BaseController._create_foodic_response({}, 400, str(ex))

        return inner

    @staticmethod
    def check_sub_merchant_permission(codes, user):
        if all(elem in user.permission_id.mapped('code') for elem in codes):
            return
        else:
            raise UnauthorizedInsufficientPermission()

    @staticmethod
    def key_authenticate(kw, lang={'language': 'en'},  is_redeem_online=False):
        key = request.httprequest.headers.get('Authorization')
        if not lang.get('language'):
            lang = 'en'
        if lang.get('language') == 'ar':
            lang = 'ar_001'
        if not key:
            raise AccessDenied()

        user = BaseController.get_user_by_api_key(key) if not is_redeem_online else BaseController.get_user_by__website_api_key(key)

        if user:
            request.uid = user.id
            # request.session.uid = user.id
            # request.session.login = user
            # request.session.session_token = user.id
            # request.session.context = dict(request.env['res.users'].context_get() or {})
            # request.session.context['uid'] = user.id
            # request.session._fix_lang(request.session.context)
            # context = request.env.context.copy()
            # context.update({'lang': lang})
            # request.env.context = context

            return user
        raise AccessDenied()

    @staticmethod
    def foodic_key_authenticate(kw, lang={'language': 'en'}):
        key = request.httprequest.headers.get('Authorization').replace("Bearer ", "", 1)
        if not lang.get('language'):
            lang = 'en'
        if lang.get('language') == 'ar':
            lang = 'ar_001'
        if not key:
            raise AccessDenied()
        user = BaseController.get_user_by_api_key(key)
        if user:
            request.uid = user.id
            # request.session.uid = user.id
            # request.session.login = user
            # request.session.session_token = user.id
            # request.session.context = dict(request.env['res.users'].context_get() or {})
            # request.session.context['uid'] = user.id
            # request.session._fix_lang(request.session.context)
            # context = request.env.context.copy()
            # context.update({'lang': lang})
            # request.env.context = context

            return user
        raise AccessDenied()

    @staticmethod
    def is_valid_url(url):
        if not url:
            return False
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    @staticmethod
    def is_valid_base64_image(image_string):
        try:
            image = base64.b64decode(image_string)
            return True
        except Exception:
            return False
