# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from odoo.tools.config import config
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessDenied
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
import logging
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.addons.redeemly_pin_management.services.notification_service import NotificationService

_logger = logging.getLogger(__name__)


class RedeemlyCronController(BaseController):
    @http.route('/private/cron_runner',
                type='json',
                auth='none',
                methods=['POST', 'OPTIONS'],
                save_session=False,
                cors='*'
                )
    def run_cronjobs(self, **kw):
        try:
            crons = request.env['ir.cron'].with_user(SUPERUSER_ID).search([('name', 'in', ['Send Gifting Emails',
                                                                                           'Mail: Email Queue Manager'
                                                                                           ])])
            for cron in crons:
                cron.method_direct_trigger()
        except Exception as e:
            pass
        return BaseController._create_response("ok")

    def _process_cron(self, crons, interval_type):
        if crons:
            for cron in crons:
                now = datetime.now()
                nextcall = cron_to_run = False

                if interval_type == 'daily' and (
                        not cron.sudo().lastcall or (now - cron.sudo().lastcall).days >= 1):
                    nextcall = (cron.sudo().lastcall or now) + relativedelta(days=1)
                    cron_to_run = True

                elif interval_type == 'weekly' and (
                        not cron.sudo().lastcall or (now - cron.sudo().lastcall).days >= 7):
                    nextcall = (cron.sudo().lastcall or now) + relativedelta(weeks=1)
                    cron_to_run = True
                elif interval_type == 'monthly':
                    diff = relativedelta(now, cron.sudo().lastcall) if cron.sudo().lastcall else False
                    months = diff.months + (diff.years * 12) if diff else 0
                    if months >= 1 or not diff:
                        nextcall = (cron.sudo().lastcall or now) + relativedelta(months=1)
                        cron_to_run = True
                if cron_to_run:
                    cron.sudo().method_direct_trigger()
                    cron.sudo().nextcall = nextcall
                    NotificationService.Send_Notification_email(self=cron)

    @http.route('/private/process_create_invoice_runner',
                type='json',
                auth='none',
                methods=['POST', 'OPTIONS'],
                save_session=False,
                cors=config.get("control_panel_url")
                )
    def run_process_create_invoice_requests(self, **kw):
        key = request.httprequest.headers.get('Authorization')
        if not key or key != 'F4BD3D579443CD9249011E02168FAB254DCA33F9C1412DB6F3DF1EDFCD70AA':
            raise AccessDenied()
        try:
            daily_cron = request.env.ref('redeemly_pin_management.daily_process_create_invoice_requests')
            if daily_cron:
                self._process_cron(daily_cron, 'daily')

            weekly_cron = request.env.ref('redeemly_pin_management.weekly_process_create_invoice_requests')
            if weekly_cron:
                self._process_cron(weekly_cron, 'weekly')

            monthly_cron = request.env.ref('redeemly_pin_management.monthly_process_create_invoice_requests')
            if monthly_cron:
                self._process_cron(monthly_cron, 'monthly')

        except Exception as e:
            return BaseController._create_response({}, 400, str(e))
        return BaseController._create_response("ok")
