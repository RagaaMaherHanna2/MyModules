import logging
from datetime import datetime, timedelta

import requests

from odoo import http, SUPERUSER_ID
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT, DATE_FORMAT
from odoo.http import request, content_disposition
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.addons.redeemly_pin_management.controllers.wallet_controller import RedeemlyWalletManagement
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied


class StatisticsController(BaseController):
    @http.route(
        "/exposed/service_provider_stats",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_sp_stats(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
        })
        from_date = validated.get('from_date')
        if not from_date:
            from_date = (datetime.now() - timedelta(days=1)).date()
        res = {}

        total_merchant = len(set(request.env['merchant.package.invites'] \
                                 .sudo().search([('product.service_provider_id', '=', request.env.user.id),
                                                 ('create_date', '>=', from_date)
                                                 ]).merchant))
        res['total_merchant_count'] = total_merchant

        sql = """
            select count(*) as order_count, sum(so.amount_total) as amount_total, 
            TO_CHAR(date(so.date_order), 'YYYY-MM-DD') as date
             from public.sale_order so
            where so.date_order >= %s
            and service_provider_id = %s
            group by date(so.date_order)
        """
        request.env.cr.execute(sql, [from_date, request.env.user.id])
        items = request.env.cr.fetchall()
        chart_data = []
        for item in items:
            chart_data.append({
                "sales_count": item[0],
                "sales_value": item[1],
                "date": item[2]
            })
        res['chart'] = chart_data
        return BaseController._create_response(res)

    @http.route(
        "/exposed/merchant_stats",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_merchant_stats(self, **kw):
        if not request.env.user.is_merchant:
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
        })
        from_date = validated.get('from_date')
        if not from_date:
            from_date = (datetime.now() - timedelta(days=1)).date()
        res = {}
        if request.env.user.is_sub_merchant:
            res['wallet_balance'] = round(RedeemlyWalletManagement.get_user_balance(request.env.user.parent_merchant),
                                          2)
        else:
            res['wallet_balance'] = round(RedeemlyWalletManagement.get_user_balance(request.env.user), 2)
        if request.env.user.is_sub_merchant:
            merchant_invite_domain = [('merchant', '=', request.env.user.parent_merchant.id)]
        else:
            merchant_invite_domain = [('merchant', '=', request.env.user.id)]
        if from_date:
            merchant_invite_domain.append(('create_date', '>=', from_date))
        res['merchant_invites'] = request.env['merchant.package.invites'].sudo().search_count(merchant_invite_domain)
        sql = """
            select sum(product_uom_qty) from sale_order so
            join sale_order_line sol
            on so.id = sol.order_id
            where 
            partner_id = %s
            and date_order >= %s
        """
        if request.env.user.is_sub_merchant:
            request.env.cr.execute(sql, [request.env.user.parent_merchant.partner_id.id, from_date])
        else:
            request.env.cr.execute(sql, [request.env.user.partner_id.id, from_date])
        pulled = request.env.cr.fetchall()
        res["pulled_quantity"] = pulled[0][0] if pulled[0][0] else 0
        if from_date:
            sql = """
                select sum(amount_total) as amount_total from public.sale_order so where 
                so.date_order >= %s
                and partner_id = %s
            """
            if request.env.user.is_sub_merchant:
                request.env.cr.execute(sql, [from_date, request.env.user.parent_merchant.partner_id.id])
            else:
                request.env.cr.execute(sql, [from_date, request.env.user.partner_id.id])
            sold_res = request.env.cr.fetchall()
            res['sold_total'] = round(sold_res[0][0], 2) if sold_res[0][0] else 0
        if request.env.user.is_sub_merchant:
            last_pull_partner_id = request.env.user.parent_merchant.partner_id.id
        else:
            last_pull_partner_id = request.env.user.partner_id.id
        sql = """
                        select date_order from public.sale_order 
                        where partner_id = %s
                        order by id desc
                        limit 1
                    """ % last_pull_partner_id
        request.env.cr.execute(sql)
        last_pull_date = request.env.cr.fetchall()
        res['last_pull_date'] = datetime.strftime(last_pull_date[0][0], DATETIME_FORMAT) if last_pull_date else None,

        return BaseController._create_response(res)

    @http.route(
        "/exposed/create_daily_income_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_daily_income_report(self, **kw):
        if not (request.env.user.is_accountant or request.env.user.is_accountant_manager):
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
            "to_date": "string",
            "sp": "number",
            "merchant": "number"
        })
        if not request.env.user.is_accountant_manager and validated.get('sp'):
            raise AccessDenied()
        from_date = datetime.strptime(validated.get('from_date'), DATE_FORMAT)
        to_date = datetime.strptime(validated.get('to_date'), DATE_FORMAT)
        sp = validated.get('sp', False)
        merchant = validated.get('merchant', False)
        report = request.env['daily.income.report'].sudo().create({
            'from_date': from_date,
            'to_date': to_date,
            'report_date': datetime.now(),
            'service_provider_id': sp,
            "merchant_id": merchant
        })
        return BaseController._create_response(report.serialize_for_api())

    @http.route(
        "/exposed/get_daily_income_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_daily_income_report(self, **kw):
        if not (request.env.user.is_accountant or request.env.user.is_accountant_manager):
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
            "to_date": "string",
            "limit": "number",
            "offset": "number",
        })
        from_date = datetime.strptime(validated.get('from_date'), DATE_FORMAT) if validated.get('from_date') else False
        to_date = datetime.strptime(validated.get('to_date'), DATE_FORMAT) if validated.get('to_date') else False
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        domain = [('create_uid', '=', request.env.user.id)]
        if from_date:
            domain.append(('from_date', '>=', from_date))
        if to_date:
            domain.append(('to_date', '<=', to_date))
        reports = request.env['daily.income.report'].sudo().search(domain, limit=limit, offset=offset,
                                                                   order='report_date desc')
        count = request.env['daily.income.report'].sudo().search_count(domain)

        return BaseController._create_response(
            {'data': [item.serialize_for_api() for item in reports], 'totalCount': count})

    @http.route(
        "/exposed/create_pull_fees_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_pull_fees_report(self, **kw):
        if not (request.env.user.is_accountant or request.env.user.is_accountant_manager):
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
            "to_date": "string",
            "sp": "number|required",
            "merchant": "number"
        })
        if not request.env.user.is_accountant_manager and validated.get('sp'):
            raise AccessDenied()
        from_date = datetime.strptime(validated.get('from_date'), DATE_FORMAT)
        to_date = datetime.strptime(validated.get('to_date'), DATE_FORMAT)
        sp = validated.get('sp')
        service_provider = request.env['res.users'].sudo().search([('id', '=', sp)])
        merchant = validated.get('merchant', False)
        report = request.env['pull.redeem.fees.report'].sudo().create({
            'from_date': from_date,
            'to_date': to_date,
            'report_date': datetime.now(),
            'service_provider_id': service_provider.id,
            'redeem_fees': service_provider.redeem_fees_value,
            'pull_fees': service_provider.fees_value,
            "merchant_id": merchant
        })
        return BaseController._create_response(report.serialize_for_api())

    @http.route(
        "/exposed/get_pull_fees_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def pull_fees_report(self, **kw):
        if not (request.env.user.is_accountant or request.env.user.is_accountant_manager):
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "from_date": "string",
            "to_date": "string",
            "limit": "number",
            "offset": "number",
        })
        from_date = datetime.strptime(validated.get('from_date'), DATE_FORMAT) if validated.get('from_date') else False
        to_date = datetime.strptime(validated.get('to_date'), DATE_FORMAT) if validated.get('to_date') else False
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        domain = [('create_uid', '=', request.env.user.id)]
        if from_date:
            domain.append(('from_date', '>=', from_date))
        if to_date:
            domain.append(('to_date', '<=', to_date))
        reports = request.env['pull.redeem.fees.report'].sudo().search(domain, limit=limit, offset=offset,
                                                                       order='report_date desc')
        count = request.env['pull.redeem.fees.report'].sudo().search_count(domain)

        return BaseController._create_response(
            {'data': [item.serialize_for_api() for item in reports], 'totalCount': count})

    @http.route(
        "/exposed/daily_pull_redeem_fees_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def daily_pull_redeem_fees_report(self, **kw):
        if not request.env.user.is_accountant_manager:
            raise AccessDenied()
        validated = BaseController.get_validated(kw, {
            "service_provider_id": "number|required",
            "merchant_id": "number|required",
            "limit": "number",
            "offset": "number",
        })
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0
        domain = []
        if validated.get('service_provider_id'):
            domain.append(('service_provider_id', '=', validated.get('service_provider_id')))
        if validated.get('merchant_id'):
            merchant_user = request.env['res.users'].sudo().search([('id', '=', validated.get('merchant_id'))])
            domain.append(('merchant_id', '=', merchant_user.partner_id.id))

        reports = request.env['daily.pull.redeem.fees.report'].sudo().search(domain, limit=limit, offset=offset,
                                                                             order='create_date desc')
        count = request.env['daily.pull.redeem.fees.report'].sudo().search_count(domain)
        return BaseController._create_response(
            {'data': [item.serialize_for_api() for item in reports], 'totalCount': count})

    @http.route(
        "/exposed/get_accountant_manager_sps",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_accountant_manager_sps(self, **kw: object) -> object:
        user = request.env.user
        if not user.is_accountant_manager:
            raise AccessDenied()

        result = user.sudo().serialize_for_api_sps(user)
        return BaseController._create_response({"data": result}, message='')

    @http.route(
        "/exposed/download_fees_report_pdf",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_fees_report_pdf(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'report')]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain)
        # logging.info(attach.ids)
        details_request = request.env['pull.redeem.fees.report'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        # logging.info(details_request.ids)
        if details_request:
            filename = 'Pull_redeem_fees_%s_%s.pdf' % (
                details_request.from_date, details_request.to_date)
            file = requests.get(attach.url, timeout=5)
            if file:
                content = file.content
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content)),
                                  ('Content-Disposition', content_disposition(filename))
                                  ]
                return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()
