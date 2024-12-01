import logging
from datetime import datetime

from odoo import http, SUPERUSER_ID
from odoo.http import request
import jwt
import time
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied
from odoo.exceptions import ValidationError


class UtilsController(BaseController):
    @http.route(
        "/exposed/get_user_by_reference",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_user_by_reference(self, **kw):
        validated = BaseController.get_validated(kw, {"reference": "string|required"})
        user = request.env['res.users'].sudo().search([('reference', '=', validated['reference'])])
        if not user:
            raise UserError('User Not Found')

        data = {
            "name": user.name
        }
        return BaseController._create_response(data)

    @http.route(
        "/exposed/check_code",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check_code(self, **kw):
        validated = BaseController.get_validated(kw, {"code": "string|required"})
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        code = request.env['package.codes'].with_user(1).search(
            ["|", ('code', '=', validated['code']), ('name', '=', validated['code'])])

        if not code:
            raise UserError("Code Not Found")
        if user.is_service_provider and not code.package.service_provider_id.id == user.id:
            raise UserError("Code Not Found")
        if user.is_merchant and not code.pulled_by.id == user.id:
            raise UserError("Code Not Found")
        data = code.serialize_for_api()

        return BaseController._create_response(data)

    @http.route(
        "/exposed/check_codes",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check_codes_file(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user or not user.is_service_provider:
            raise AccessDenied()
        codes = kw.get('codes')
        if not codes or not isinstance(codes, list):
            raise ValidationError(f'codes is missing')
        if len(codes) > 500000:
            raise ValidationError(f'codes is too long')
        for index in range(len(codes)):
            code = codes[index]
            if not isinstance(code, str):
                raise ValidationError(f'code {index + 1} is not valid')

        found_codes = request.env['package.codes'].with_user(1).search(
            ["&", "|", ('code', 'in', codes), ('name', "in", codes), ("package.service_provider_id", "=", user.id)])
        found_masks = {code['code']: code for code in found_codes}
        found_pins = {code['name']: code for code in found_codes}
        data = []
        for code in codes:
            found = found_masks.get(code) if found_masks.get(code) else found_pins.get(code)
            if not found:
                data.append({
                    "code": code,
                    "found": False
                })
            else:
                result = found.serialize_for_api()
                result['found'] = True
                data.append(result)

        return BaseController._create_response(data)
