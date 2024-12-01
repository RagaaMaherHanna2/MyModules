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
        "/exposed/auth/create_sub_merchant_account",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_sub_merchant_account(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "name": "string|required",
                "email": "string|required",
                "password": "string|required"
            },
        )
        user = request.env.user
        if user.is_merchant and not user.is_sub_merchant:
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
                        "is_sub_merchant": True,
                        "parent_merchant": user.id,
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
        "/exposed/auth/get_new_sub_merchants",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_new_sub_merchants(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "offset": "number",
                "limit": "number",
                "id": "number",
                "reference": "string"
            },
        )
        user = request.env.user
        if not user.is_merchant and user.is_sub_merchant:
            raise AccessDenied()
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0

        domain = ['&', '&', ('create_uid', '=', user.id),
                  ('is_merchant', '=', True),
                  ('is_sub_merchant', '=', True)
                  ]

        if validated.get("id"):
            domain.append(('id', '=', validated.get('id')))
        if validated.get('reference'):
            domain.append(('reference', '=', validated.get('reference')))

        data = request.env['res.users'].sudo().search(domain, limit=limit, offset=offset)
        count = request.env['res.users'].sudo().search_count(domain)
        result = [item.serialize_for_api(item.id) for item in data]
        return BaseController._create_response({"data": result, "totalCount": count}, message='')

    @http.route("/exposed/list_permission",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_group_permission_list(self, **kw):
        if not request.env.user.is_merchant or   request.env.user.is_sub_merchant:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"code": "string", "offset": "int", "limit": "int","sub_merchant" : "string", "permission_id": "number"},
        )
        domain = []
        code = validated.get("code")
        permission_id = validated.get("permission_id")
        offset = validated.get('offset')
        limit = validated.get("limit")
        sub_merchant = validated.get("sub_merchant")
        if not sub_merchant:
            raise UserError("Sub Merchant Value Missing")

        sub_merchant_user = request.env['res.users'].with_user(1).search([('reference', '=', sub_merchant)])
        if not sub_merchant_user or  not sub_merchant_user.is_merchant or not sub_merchant_user.is_sub_merchant:
            raise UserError("Sub Merchant Value Not Correct")

        if code:
            domain += [('code', 'ilike', code)]
        if permission_id:
            domain += [('id', '=', permission_id)]
        groups = request.env['sub.merchant.permission'].with_user(1).search(domain, limit=limit, offset=offset,
                                                               order="create_date desc")
        groups_count = request.env['sub.merchant.permission'].with_user(1).search_count(domain)
        data = []
        for group in groups:
            data.append(group.serialize_for_api(sub_merchant_user.id))
        res = {'data': data, 'totalCount': groups_count}
        return BaseController._create_response(res)

    @http.route("/exposed/assign_permission_to_submerchant",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def assign_permission_to_submerchant(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_merchant or user.is_sub_merchant:
            raise AccessDenied()
        invite_data = BaseController.get_validated(
            kw,
            {
                "sub_merchant": "string|required",
                "codes": "list",

            },
            req_only=True
        )

        codes = []
        for line in invite_data['codes']:
            validated = BaseController.get_validated(
                line,
                {
                    "code": "string|required",
                    "enable": "boolean|required"
                },
                req_only=True
            )
            codes.append(validated)

        sub_merchant = request.env['res.users'].with_user(1).search([
            ("reference", "=", invite_data['sub_merchant']),
            ("is_merchant", '=', True),
            ("is_sub_merchant" , "=" , True)
        ])

        if not sub_merchant:
            raise UserError("Sub Merchant Not Found")

        for item in codes:
            if item["enable"] == True:
                permission_id = request.env['sub.merchant.permission'].with_user(1).search([
                    ("code", "=", item['code']),
                ])
                # if not permission_id:
                #     raise UserError("Permission Not Found")
                if permission_id.id in sub_merchant.permission_id.ids:
                    continue
                sub_merchant.permission_id = [(4, permission_id.id)]
            else:
                permission_id = request.env['sub.merchant.permission'].with_user(1).search([
                    ("code", "=", item['code']),
                ])
                # if not permission_id:
                #     raise UserError("Permission Not Found")
                if permission_id.id in sub_merchant.permission_id.ids:
                    sub_merchant.permission_id -= permission_id
                    sub_merchant.write({'permission_id': [(6, 0, sub_merchant.permission_id.ids)]})

        return BaseController._create_response([item.serialize_for_api( sub_merchant.id ) for item in sub_merchant.permission_id], 200, "Permissions Added Successfully .")

