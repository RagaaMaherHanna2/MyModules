import logging
from datetime import datetime
from odoo.http import request
from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError


class SettingController(BaseController):
    @http.route(
        "/exposed/update_settings",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def update_setting(self, **kw):
        setting = BaseController.get_validated(kw, {"stock_limit": "number", "sp_hash": "string", "balance_limit": "number",
                                                    "enable_low_stock_notification": "boolean",
                                                    "enable_low_balance_notification": "boolean",
                                                    "balance_notification_to_email": "string",
                                                    "stock_notification_to_email": "string",
                                                    })
        if 'stock_limit' in setting:
            request.env.user.stock_limit = setting.get('stock_limit')
        if 'enable_low_stock_notification' in setting:
            request.env.user.enable_low_stock_notification = setting.get('enable_low_stock_notification')
        if 'balance_limit' in setting:
            request.env.user.balance_limit = setting.get('balance_limit')
        if 'enable_low_balance_notification' in setting:
            request.env.user.enable_low_balance_notification = setting.get('enable_low_balance_notification')
        if 'balance_notification_to_email' in setting:
            request.env.user.balance_notification_to_email = setting.get('balance_notification_to_email')
        if 'stock_notification_to_email' in setting:
            request.env.user.notification_to_email = setting.get('stock_notification_to_email')



        if setting.get('sp_hash'):
            if len(setting.get('sp_hash')) < 36:
                raise UserError("Hash Should be more than 36 character")
            request.env.user.sp_hash = setting.get('sp_hash')
        return BaseController._create_response("ok", message='Setting updated successfully')

    @http.route(
        "/exposed/get_settings",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_setting(self, **kw):
        res = {
            "enable_low_stock_notification": request.env.user.enable_low_stock_notification,
            "stock_limit": request.env.user.stock_limit,
            "stock_notification_to_email": request.env.user.notification_to_email,
            "enable_low_balance_notification": request.env.user.enable_low_balance_notification,
            "balance_limit": request.env.user.balance_limit,
            "balance_notification_to_email": request.env.user.balance_notification_to_email,
        }
        return BaseController._create_response(data=res)