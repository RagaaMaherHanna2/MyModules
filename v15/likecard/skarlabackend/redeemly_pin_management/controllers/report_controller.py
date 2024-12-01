from PIL.ImageChops import offset
from dateutil.relativedelta import relativedelta

from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT, DATE_FORMAT
from datetime import datetime, time
from odoo.http import request, content_disposition
from odoo import http, SUPERUSER_ID, _
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.tools.config import config
from odoo.exceptions import UserError, AccessDenied, ValidationError
import requests

import logging

_logger = logging.getLogger(__name__)


class ReportController(BaseController):

    @staticmethod
    def create_detail_sales_report_record(user_id, from_date, to_date, merchant=False, product=False):
        return request.env['detail.sales.report'].sudo().create({
            'user_id': user_id,
            'report_date': datetime.now(),
            'from_date': datetime.strptime(from_date, DATE_FORMAT),
            'to_date': datetime.strptime(to_date, DATE_FORMAT),
            "merchant_filter": merchant.id if merchant else False,
            "product": product
        })

    @http.route(
        "/exposed/create_detail_sales_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def create_detail_sales_report(self, **kw):
        user = request.env.user
        if not user or (not user.is_service_provider and not user.is_merchant):
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"from_date": "string|required", "to_date": "string|required",
             "product": "number", "merchant_filter": "string"}
        )

        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["2.1"], user=user)
            user_id = user.parent_merchant.id
        else:
            user_id = request.uid

        if validated.get("merchant_filter"):
            merchant = request.env['res.users'].sudo().search([('reference', '=', validated["merchant_filter"])])
        else:
            merchant = False
        order = self.create_detail_sales_report_record(user_id=user_id,
                                                       from_date=validated['from_date'], to_date=validated['to_date'],
                                                       merchant=merchant, product=validated.get('product'))

        return BaseController._create_response(data=order.serialize_for_api())

    @http.route(
        "/exposed/get_detail_sales_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_detail_sales_report(self, **kw):
        user = request.env.user
        if not user or (not user.is_service_provider and not user.is_merchant):
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {'limit': "number", "offset": "number", "from_date": "string", "to_date": "string",
             "product": "string", "merchant_filter": "number"}
        )

        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["2.2"], user=user)
            domain = [('user_id', '=', user.parent_merchant.id)]
        else:
            domain = [('user_id', '=', request.uid)]
        if validated.get('from_date'):
            domain.append(('report_date', '>=', validated['from_date']))
        if validated.get('to_date'):
            domain.append(('report_date', '<=', validated['to_date']))
        if validated.get('product'):
            domain.append(('product.name', 'like', validated.get('product')))
        if validated.get('merchant_filter'):
            domain.append(('merchant_filter', '=', validated.get('merchant_filter')))
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get("limit") else 20
        _logger.info('domain:%s', domain)
        details_request = request.env['detail.sales.report'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                                 order="create_date desc")
        request_count = request.env['detail.sales.report'].with_user(1).search_count(domain)
        _logger.info('details_request:%s', details_request)
        _logger.info('request_count:%s', request_count)
        data = []
        for rq in details_request:
            data.append(rq.serialize_for_api())
            _logger.info('for%s is %s', rq, data)
        res = {
            'data': data,
            'totalCount': request_count
        }
        return BaseController._create_response(data=res)

    @http.route(
        "/exposed/get_accountant_manager_sps_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_accountant_manager_sps_report(self, **kw):
        user = request.env.user
        data = []
        if not user or not user.is_accountant_manager:
            raise AccessDenied()
        accountant_manager_sps_ids = user.accountant_manager_sps_ids.ids
        if not accountant_manager_sps_ids:
            return BaseController._create_response(data=data, message="You Don't have any service providers!!")

        user_rec = request.env['res.users'].sudo()
        validated = BaseController.get_validated(
            kw,
            {'limit': "number", "offset": "number", "id": "number", "name": "string"})

        if validated.get('id'):
            if validated.get('id') not in accountant_manager_sps_ids:
                raise AccessDenied()
            sps = user_rec.browse(validated.get('id'))
            request_count = 1

        else:
            domain = [('id', 'in', accountant_manager_sps_ids)]
            if validated.get('name'):
                domain.append(('name', 'ilike', validated['name']))
            sps = user_rec.search(domain,
                                  offset=validated.get('offset') or 0,
                                  limit=validated.get('limit') or 20)
            request_count = user_rec.search_count(domain)
        if sps:
            prod_rec = request.env['product.template'].sudo()
            for sp in sps:
                sp_merchants = user_rec.search(['|', '&', ('create_uid', '=', sp.id),
                                                ('is_merchant', '=', True),
                                                ('invites_ids.product.service_provider_id', '=', sp.id)
                                                ])
                sp_products = prod_rec.search(
                    [('service_provider_id', '=', sp.id), ("is_redeemly_product", "=", True)])
                data.append({
                    'sp_id': sp.id,
                    'sp_name': sp.name,
                    'sp_merchants': [{'mer_id': mer.id, 'mer_name': mer.name} for mer in sp_merchants],
                    'sp_merchants_count': len(sp_merchants),
                    'sp_products': [{'prod_id': prod.id, 'prod_name': prod.name} for prod in sp_products],
                    'sp_products_count': len(sp_products),
                })

        res = {
            'data': data,
            'totalCount': request_count
        }
        return BaseController._create_response(data=res)

    @http.route(
        "/exposed/get_accountant_manager_sps_sales_report",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_accountant_manager_sps_sales_report(self, **kw):
        user = request.env.user
        data = []
        if not user or not user.is_accountant_manager:
            raise AccessDenied()
        accountant_manager_sps_ids = user.accountant_manager_sps_ids.ids
        if not accountant_manager_sps_ids:
            return BaseController._create_response(data=data, message="You Don't have any service providers!!")

        user_rec = request.env['res.users'].sudo()
        validated = BaseController.get_validated(
            kw,
            {'limit': "number", "offset": "number",
             "id": "number", "name": "string", "from_date": "string|required", "to_date": "string|required",
             })

        if validated.get('id'):
            if validated.get('id') not in accountant_manager_sps_ids:
                raise AccessDenied()
            sps = request.env['res.users'].sudo().browse(validated.get('id'))
            request_count = 1

        else:
            domain = [('id', 'in', accountant_manager_sps_ids)]
            if validated.get('name'):
                domain.append(('name', 'ilike', validated['name']))
            sps = user_rec.search(domain,
                                  offset=validated.get('offset') or 0,
                                  limit=validated.get('limit') or 20)
            request_count = user_rec.search_count(domain)
        if sps:
            datetime_from = datetime.strptime(validated['from_date'], DATE_FORMAT).replace(hour=0, minute=0,
                                                                                               second=0,
                                                                                               microsecond=0)
            datetime_to = datetime.strptime(validated['to_date'], DATE_FORMAT).replace(hour=23, minute=59,
                                                                                           second=59,
                                                                                           microsecond=999999)

            difference = relativedelta(datetime_to, datetime_from)
            months_difference = difference.years * 12 + difference.months
            if months_difference > 1:
                raise ValidationError(_("Dates difference max is only one month."))
            query = """
                SELECT
                    sp.id AS service_provider_id,
                    COUNT(so.id) AS order_count
                FROM
                    res_users sp
                LEFT JOIN
                    sale_order so ON so.service_provider_id = sp.id
                    AND so.date_order >= %s
                    AND so.date_order <= %s
                WHERE
                    sp.id IN %s
                GROUP BY
                    sp.id
            """
            params = (datetime_from, datetime_to, tuple(sps.ids))
            request.env.cr.execute(query, params)
            data = request.env.cr.dictfetchall()
            service_provider_names = {sp.id: sp.name for sp in sps}
            for d in data:
                d.update({'service_provider_name': service_provider_names.get(d['service_provider_id'], 'Unknown')})

        res = {
            'data': data,
            'totalCount': request_count
        }
        return BaseController._create_response(data=res)

    @http.route(
        "/exposed/download_detail_sales_report",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_detail_sales_report(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'report_excel')]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain, limit=1)
        details_request = request.env['detail.sales.report'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        if details_request:
            filename = 'sales_report_%s_%s.xlsx' % (
                details_request.from_date, details_request.to_date)
            file = requests.get(attach.url, timeout=5)
            if file:
                content = file.content
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content)),
                                  ('Content-Disposition', content_disposition(filename))
                                  ]
                return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()
