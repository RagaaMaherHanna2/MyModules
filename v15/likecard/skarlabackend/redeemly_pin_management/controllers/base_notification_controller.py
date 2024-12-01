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
        "/exposed/auth/get_notifications",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_notifications(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "offset": "number",
                "limit": "number",
                "id": "number",
                "is_read":"boolean"
            },
        )
        user = request.env.user
        # if not user.is_merchant and user.is_sub_merchant:
        #     raise AccessDenied()
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        if request.env.user.is_merchant and not request.env.user.is_sub_merchant:
            partner_id = request.env.user.partner_id.id
            # partner_id = request.env.user.create_uid.partner_id.id
        elif request.env.user.is_sub_merchant:
            partner_id = request.env.user.create_uid.partner_id.id
        else:
            partner_id = request.env.user.partner_id.id


        domain = [ ('author_id', '=', partner_id),
                  ('model', 'in',
                   ['pin.management.bank.transfer.request' ,
                    'merchant.invoice.request',
                    'merchant.package.invites'
                    ]),
                   ('skarla_dashboard', '=', True)

                  ]

        if validated.get("id"):
            domain.append(('id', '=', validated.get('id')))

        if validated.get("is_read") != None:
            domain.append(('is_read', '=', validated.get('is_read')))

        data = request.env['mail.message'].sudo().search(domain, limit=limit, offset=offset)
        count = request.env['mail.message'].sudo().search_count(domain)
        result = [item.serialize_for_api() for item in data]
        return BaseController._create_response({"data": result, "totalCount": count}, message='')

    @http.route("/exposed/auth/set_notifycation_readed",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def set_notifycation_readed(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "ids": "list",
            },
        )



        ids = validated.get("ids")

        message = request.env['mail.message'].with_user(1).search([('id', 'in', ids)])
        if not message:
            raise UserError("Message notification Not Found")
        for item in message:
            if request.env.user.is_sub_merchant:
                if request.env.user.parent_merchant.partner_id.id != item.author_id.id:
                    raise UserError("Message notification Not Found")
            elif request.env.user.partner_id.id != item.author_id.id:
                raise UserError("Message notification Not Found")
        data = []
        for item in message:
            item.is_read = True
            data.append(item.serialize_for_api())
        res = {'is_read': True, 'data': data}
        return BaseController._create_response(res)

