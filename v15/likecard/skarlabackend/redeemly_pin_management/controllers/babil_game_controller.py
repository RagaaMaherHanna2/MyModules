import datetime
import hmac
import hashlib
import string

from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.http import request
import requests

from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
import json
from odoo.tools.config import config
from odoo.addons.redeemly_pin_management.controllers.redeem_controller import RedeemController
from odoo.exceptions import UserError, AccessDenied
from random import randint


class BabilGameController(BaseController):
    @http.route(
        "/babil_game/check",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def check(self, **kw):
        user = BaseController.key_authenticate(kw)
        validated = BaseController.get_validated(kw, {"codes": "list|required", 'sp_hash': 'string|required'})

        hash_user = request.env['res.users'].with_user(1).search([('sp_hash', '=', validated['sp_hash'])])
        if user.id != hash_user.id:
            raise UserError("Invalid Request")
        res = RedeemController.check_code_with_hash_func(user=user, param=validated, required_sku=False)
        return res

    @http.route(
        "/babil_game/redeem",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def redeem(self, **kw):
        user = BaseController.key_authenticate(kw)
        if not kw.get('sp_hash') or not isinstance(kw.get('sp_hash'), str):
            raise AccessDenied()

        hash_user = request.env['res.users'].with_user(1).search([('sp_hash', '=', kw.get('sp_hash'))])
        if user.id != hash_user.id:
            raise UserError("Invalid Request")
        # if not kw.get('sku'):
        #     raise UserError("Missing SKU")
        return RedeemController.redeem_func(kw, user)

    @http.route(
        "/babil_game/get_sales_report",
        type="json",
        auth="none",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_babil_sales_report(self, **kw):
        user = BaseController.key_authenticate(kw)
        if not kw.get('sp_hash') or not isinstance(kw.get('sp_hash'), str):
            raise AccessDenied()

        hash_user = request.env['res.users'].with_user(1).search([('sp_hash', '=', kw.get('sp_hash'))])
        if user.id != hash_user.id:
            raise UserError("Invalid Request")

        validated = BaseController.get_validated(kw, {"from_date": "string|required",
                                                      'to_date': 'string|required',
                                                      'state': 'string',
                                                      'offset': "number",
                                                      "limit": "number"
                                                      })
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        if limit > 10000:
            raise UserError("Invalid Limit Maximum 10,000")
        if validated.get('state'):
            serials = request.env['product.serials'].sudo().search([('pull_date', '>=', validated['from_date']),
                                                                ('pull_date', '<=', validated['to_date']),
                                                                ('state', '=', validated['state']),
                                                                ('product_id.service_provider_id', '=', user.id)
                                                                ], limit=limit, offset=offset)
        elif not validated.get('state'):
            serials = request.env['product.serials'].sudo().search([('pull_date', '>=', validated['from_date']),
                                                                    ('pull_date', '<=', validated['to_date']),
                                                                    ('product_id.service_provider_id', '=', user.id)
                                                                    ], limit=limit, offset=offset)

        data = []

        for serial in serials:
            # hist_date = redeemed_history.filtered(lambda v: v.product_serial.id == serial.id)
            data.append({
                'product': {
                    'id': serial.product_id.id,
                    'name': serial.product_id.name,
                    'sku': serial.product_id.SKU
                },
                'serial_number': serial.serial_number,
                'price': serial.order_id.order_line.filtered(
                    lambda v: v.product_id.id == serial.product_id.id).price_unit,
                'merchant': {
                    'name': serial.pulled_by.name,
                    'reference': serial.pulled_by.reference
                },
                'state': BabilGameController.get_serial_label(serial.state),
                'pull_date': datetime.datetime.strftime(serial.pull_date, DATETIME_FORMAT),
                'redeem_date': datetime.datetime.strftime(serial.redeem_history_prepaid_ids[0].date, DATETIME_FORMAT)
                if len(serial.redeem_history_prepaid_ids) > 0 else False,
            })
        return BaseController._create_response(data=data, message="")

    @staticmethod
    def get_serial_label(state):
        if state == '1':
            return 'Available'
        if state == '2':
            return 'Reserved'
        if state == '3':
            return 'Pulled'
        if state == '5':
            return 'Redeemed'
        if state == '4':
            return 'Expired'
