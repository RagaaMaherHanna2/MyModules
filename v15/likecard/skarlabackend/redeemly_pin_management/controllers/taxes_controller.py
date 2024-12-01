import uuid
from datetime import datetime, timezone
import requests
from odoo.http import route, content_disposition
import json
from odoo.http import request
from odoo.tools import config
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.addons.redeemly_pin_management.services.code_validation_service import RedeemlyCodeValidationService
from odoo.addons.redeemly_pin_management.services.redeem_service import RedeemService
from odoo import _, SUPERUSER_ID
from hashlib import sha256


class TaxController(BaseController):
    @route("/exposed/list_taxes",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_taxes_list(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"name": "string", "offset": "int", "limit": "int", "tax_id": "number"},
        )
        domain = [('service_provider_id', '=', request.uid), ("is_merchant", "=", True)]
        name = validated.get("name")
        tax_id = validated.get("tax_id")
        offset = validated.get('offset')
        limit = validated.get("limit")
        if name:
            domain += [('name', 'ilike', name)]
        if tax_id:
            domain += [('id', '=', tax_id)]
        taxes = request.env['account.tax'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                       order="create_date desc")
        tax_count = request.env['account.tax'].with_user(1).search_count(domain)
        data = []
        for tax in taxes:
            data.append(tax.serialize_for_api())
        res = {'data': data, 'totalCount': tax_count}
        return BaseController._create_response(res)

    @route("/exposed/create_tax",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_taxes(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()

        tax_data = BaseController.get_validated(
            kw,
            {
                "name" : "string",
                "amount" : "number",
                "amount_type": "string"
            },
        )

        if not tax_data.get('name') \
            or not tax_data.get('amount') \
            or not tax_data.get('amount_type') :
            raise UserError("Missing Val")
        tax = request.env['account.tax'].sudo().search(
            [
                ('is_merchant', '=', True),
                ('service_provider_id', '=', request.uid),
                ('amount_type', '=', tax_data["amount_type"]),
                ('amount', '=', tax_data['amount'])
            ]
        )
        if len(tax) == 0:
            old_tax = request.env['account.tax'].sudo().search(
                [
                    ('is_merchant', '=', True),
                ]
            )[0]
            tax_data["service_provider_id"] = request.uid
            tax = old_tax.sudo().copy()
            tax.write(
                tax_data
            )
        else:
            raise UserError("Account Tax Already Founded")
        return BaseController._create_response(tax.serialize_for_api())