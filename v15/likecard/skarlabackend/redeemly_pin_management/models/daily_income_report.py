import base64
import logging
from datetime import datetime, timedelta

from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT

from odoo import models, fields
from odoo.tools import config

_logger = logging.getLogger(__name__)


class DailyIncomeReport(models.Model):
    _name = 'daily.income.report'
    report_date = fields.Datetime()
    report = fields.Binary(string='Report Pdf')
    from_date = fields.Datetime()
    to_date = fields.Datetime()
    merchant_id = fields.Many2one('res.users', string='Merchant',
                                  domain=[('is_merchant', '=', True)], index=True)
    service_provider_id = fields.Many2one('res.users', string='Service Provider',
                                          domain=[('is_service_provider', '=', True)], index=True)

    def get_public_url(self):
        self.ensure_one()
        url = self.get_file_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param('s3.obj_url')
        return url.replace(base_url, "/exposed/download_report_pdf?file_hash=") if url else False

    def get_file_url(self):
        attachment = self.env['ir.attachment'].search(
            [("res_model", "=", self._name), ('res_id', '=', self.id), ('res_field', '=', 'report')])
        return attachment.url if attachment else False

    def serialize_for_api(self):
        return {
            'from_date': datetime.strftime(self.from_date, DATETIME_FORMAT) if self.from_date else False,
            'to_date': datetime.strftime(self.to_date, DATETIME_FORMAT) if self.to_date else False,
            'report_url': self.get_public_url(),
            'report_date': datetime.strftime(self.report_date, DATETIME_FORMAT) if self.report_date else False,
            'service_provider_id': self.service_provider_id.id if self.service_provider_id else False,
            'service_provider_name': self.service_provider_id.name if self.service_provider_id else False,
            'merchant_id': self.merchant_id.id if self.merchant_id else False,
            'merchant_name': self.merchant_id.name if self.merchant_id else False,
        }

    def daily_income_report_cron(self):
        try:
            reports = self.search([('report', '=', False)])
            for new_daily_report in reports:
                now = datetime.now().today()
                yesterday = now - timedelta(days=1)
                if not new_daily_report.from_date and not new_daily_report.to_date:
                    from_date = datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day)
                    to_date = datetime(year=now.year, month=now.month, day=now.day)
                    new_daily_report.from_date = from_date
                    new_daily_report.to_date = to_date
                if new_daily_report.service_provider_id:
                    if new_daily_report.merchant_id:
                        sql = """
                            select so.service_provider_id, partner.name, sum(so.amount_total) as amount_total from public.sale_order so
                            join res_users usr on usr.id = so.service_provider_id
                            join res_partner partner on partner.id = usr.partner_id
                            where so.service_provider_id = %s and so.date_order >= %s
                            and so.date_order <= %s
                            and so.partner_id = %s
                            group by so.service_provider_id, partner.name
                                                """
                        self.env.cr.execute(sql, (
                            new_daily_report.service_provider_id.id, new_daily_report.from_date,
                            new_daily_report.to_date,
                            new_daily_report.merchant_id.partner_id.id))
                    else:
                        sql = """
                        select so.service_provider_id, partner.name, sum(so.amount_total) as amount_total from public.sale_order so
                        join res_users usr on usr.id = so.service_provider_id
                        join res_partner partner on partner.id = usr.partner_id
                        where so.service_provider_id = %s and so.date_order >= %s
                        and so.date_order <= %s
                        group by so.service_provider_id, partner.name
                        """
                        self.env.cr.execute(sql, (
                            new_daily_report.service_provider_id.id, new_daily_report.from_date,
                            new_daily_report.to_date))
                else:
                    sql = """
                                        select so.service_provider_id, partner.name, sum(so.amount_total) as amount_total from public.sale_order so
                                        join res_users usr on usr.id = so.service_provider_id
                                        join res_partner partner on partner.id = usr.partner_id
                                        where so.date_order >= %s
                                        and so.date_order <= %s
                                        group by so.service_provider_id, partner.name
                                        """
                    self.env.cr.execute(sql, (new_daily_report.from_date, new_daily_report.to_date))

                query_result = self.env.cr.dictfetchall()
                if query_result:
                    qr_pdf = \
                        self.env.ref('redeemly_pin_management.daily_income_report')._render_qweb_pdf(
                            res_ids=new_daily_report.ids,
                            data={"data": query_result})[0]

                    new_daily_report.report = base64.b64encode(qr_pdf)
                    template = self.env.ref('redeemly_pin_management.daily_income_email_template')

                    email_values = {
                        'email_from': 'noreply@skarla.com'
                    }
                    context = {'data': query_result, 'server_base_url': config.get('server_base_url')}
                    # template.with_context(context).send_mail(new_daily_report.id, email_values=email_values)
        except Exception as e:
            _logger.info("skarla_cron daily income report")
            _logger.exception(e)
            self.env.cr.rollback()

    def _daily_income_report_get_line(self, sp_id):
        sql = """
               select so.partner_id, partner.name, sum(so.amount_total) as amount_total from public.sale_order so
               join res_partner partner on partner.id = so.partner_id
               where so.date_order >= %s
               and so.date_order < %s
               and so.service_provider_id = %s
               group by so.partner_id, partner.name
               """
        self.env.cr.execute(sql, (self.from_date, self.to_date, sp_id))

        return self.env.cr.dictfetchall()


class PullRedeemFeesReport(models.Model):
    _name = 'pull.redeem.fees.report'
    report_date = fields.Datetime()
    report = fields.Binary(string='Report Pdf')
    is_no_data = fields.Boolean(string="Is No Data")
    from_date = fields.Datetime()
    to_date = fields.Datetime()
    pull_fees = fields.Float(string='Pull Fees', digits=(10, 7))
    redeem_fees = fields.Float(string='Redeem Fees')
    merchant_id = fields.Many2one('res.users', string='Merchant',
                                  domain=[('is_merchant', '=', True)], index=True)
    service_provider_id = fields.Many2one('res.users', string='Service Provider',
                                          domain=[('is_service_provider', '=', True)], index=True)

    exchange_rate = fields.Float(compute='_compute_exchange_rate', string='Exchange Rate')

    def _compute_exchange_rate(self):

        self.exchange_rate = self.env['res.currency'].search([('name', '=', 'AED')],
                                                             limit=1).rate

    def get_public_url(self):
        self.ensure_one()
        url = self.get_file_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param('s3.obj_url')
        return url.replace(base_url, "/exposed/download_fees_report_pdf?file_hash=") if url else False

    def get_file_url(self):
        attachment = self.env['ir.attachment'].search(
            [("res_model", "=", self._name), ('res_id', '=', self.id), ('res_field', '=', 'report')])
        return attachment.url if attachment else False

    def serialize_for_api(self):
        return {
            'from_date': datetime.strftime(self.from_date, DATETIME_FORMAT) if self.from_date else False,
            'to_date': datetime.strftime(self.to_date, DATETIME_FORMAT) if self.to_date else False,
            'report_url': self.get_public_url(),
            'is_no_data': self.is_no_data,
            'redeem_fees': self.redeem_fees,
            'pull_fees': self.pull_fees,
            'report_date': datetime.strftime(self.report_date, DATETIME_FORMAT) if self.report_date else False,
            'service_provider_id': self.service_provider_id.id if self.service_provider_id else False,
            'service_provider_name': self.service_provider_id.name if self.service_provider_id else False,
            'merchant_id': self.merchant_id.id if self.merchant_id else False,
            'merchant_name': self.merchant_id.name if self.merchant_id else False,
        }

    def pull_redeem_fees_report_cron(self):
        try:
            reports = self.search([('report', '=', False)])

            for new_daily_report in reports:
                if new_daily_report.service_provider_id:
                    if new_daily_report.merchant_id:
                        sql = """
                            select 'Pull' as operation, so.service_provider_id, 
                            partner.name sp_name,merchant.name m_name, sum(sol.product_uom_qty) as count
                            from public.sale_order so
                            join public.sale_order_line sol on sol.order_id = so.id
                            join res_users usr on usr.id = so.service_provider_id
                            join res_partner partner on partner.id = usr.partner_id
                            join res_partner merchant on merchant.id = so.partner_id
                            where so.service_provider_id = %s and so.date_order >= %s
                            and so.date_order <= %s
                            and so.partner_id = %s
                            group by so.service_provider_id, partner.name, merchant.name
                            union all
                            select 'Redeem' as operation, so.service_provider_id, 
                            partner.name sp_name,merchant.name m_name, count(*) as count 
                            from public.redeem_history_prepaid hist
                                join public.product_serials ps on ps.id = hist.product_serial
                                join public.sale_order so on so.id = ps.order_id
                                join res_users usr on usr.id = so.service_provider_id
                                join res_partner partner on partner.id = usr.partner_id
                                join res_partner merchant on merchant.id = so.partner_id
                                where so.service_provider_id = %s and so.date_order >= %s
                                and so.date_order <= %s
                                and so.partner_id = %s
                                and ps.state = '5'
                                group by so.service_provider_id, partner.name, merchant.name  
                                                """

                        self.env.cr.execute(sql, (
                            new_daily_report.service_provider_id.id, new_daily_report.from_date,
                            new_daily_report.to_date,
                            new_daily_report.merchant_id.partner_id.id,
                            new_daily_report.service_provider_id.id, new_daily_report.from_date,
                            new_daily_report.to_date,
                            new_daily_report.merchant_id.partner_id.id
                        ))
                    else:
                        sql = """
                        select 'Pull' as operation, so.service_provider_id,
                         partner.name sp_name,merchant.name m_name, sum(sol.product_uom_qty) as count
                            from public.sale_order so
                                join public.sale_order_line sol on sol.order_id = so.id
                                join res_users usr on usr.id = so.service_provider_id
                                join res_partner partner on partner.id = usr.partner_id
                                join res_partner merchant on merchant.id = so.partner_id
                                where so.service_provider_id = %s and so.date_order >= %s
                                and so.date_order <= %s
                            group by so.service_provider_id, partner.name, merchant.name
                            union all
                            select 'Redeem' as operation, so.service_provider_id, 
                            partner.name sp_name,merchant.name m_name, count(*) as count 
                            from public.redeem_history_prepaid hist
                                join public.product_serials ps on ps.id = hist.product_serial
                                join public.sale_order so on so.id = ps.order_id
                                join res_users usr on usr.id = so.service_provider_id
                                join res_partner partner on partner.id = usr.partner_id
                                join res_partner merchant on merchant.id = so.partner_id
                                where so.service_provider_id = %s and so.date_order >= %s
                                and so.date_order <= %s
                                and ps.state = '5'
                            group by so.service_provider_id, partner.name, merchant.name
                        """
                        self.env.cr.execute(sql, (new_daily_report.service_provider_id.id,
                                                  new_daily_report.from_date, new_daily_report.to_date,
                                                  new_daily_report.service_provider_id.id,
                                                  new_daily_report.from_date, new_daily_report.to_date
                                                  ))

                query_result = self.env.cr.dictfetchall()
                if query_result:
                    qr_pdf = \
                        self.env.ref('redeemly_pin_management.pull_redeem_report')._render_qweb_pdf(
                            res_ids=new_daily_report.ids,
                            data={"data": query_result})[0]

                    new_daily_report.report = base64.b64encode(qr_pdf)
                    # template = self.env.ref('redeemly_pin_management.pull_redeem_report_template')
                    #
                    # email_values = {
                    #     'email_from': 'noreply@skarla.com'
                    # }
                    # context = {'data': query_result, 'server_base_url': config.get('server_base_url')}
                    # # template.with_context(context).send_mail(new_daily_report.id, email_values=email_values)
                else:
                    new_daily_report.is_no_data = True
        except Exception as e:
            _logger.info("skarla_cron daily income report")
            _logger.exception(e)
            self.env.cr.rollback()

    def _get_line(self, sp_id):
        sql = """
               select so.partner_id, partner.name, sum(so.amount_total) as amount_total from public.sale_order so
               join res_partner partner on partner.id = so.partner_id
               where so.date_order >= %s
               and so.date_order < %s
               and so.service_provider_id = %s
               group by so.partner_id, partner.name
               """
        self.env.cr.execute(sql, (self.from_date, self.to_date, sp_id))

        return self.env.cr.dictfetchall()


class DailyPullRedeemFeesReport(models.Model):
    _name = 'daily.pull.redeem.fees.report'

    report_date = fields.Datetime()
    service_provider_id = fields.Many2one('res.users', string='Service Provider', index=True)
    merchant_id = fields.Many2one('res.partner', string='Merchant', index=True)
    pull_fees_count = fields.Float()
    pull_fees_total = fields.Float()
    redeem_fees_count = fields.Float()
    redeem_fees_total = fields.Float()

    def serialize_for_api(self):
        return {
            'report_date': datetime.strftime(self.report_date, DATETIME_FORMAT) if self.report_date else False,
            'service_provider_id': self.service_provider_id.id if self.service_provider_id else False,
            'service_provider_name': self.service_provider_id.name if self.service_provider_id else '',
            'merchant_id': self.merchant_id.id if self.merchant_id else False,
            'merchant_name': self.merchant_id.name if self.merchant_id else '',
            'pull_fees_count': self.pull_fees_count if self.pull_fees_count else 0.0,
            'pull_fees_total': self.pull_fees_total if self.pull_fees_total else 0.0,
            'redeem_fees_count': self.redeem_fees_count if self.redeem_fees_count else 0.0,
            'redeem_fees_total': self.redeem_fees_total if self.redeem_fees_total else 0.0,
        }

    def daily_pull_redeem_fees_cron(self):
        now = datetime.now().today()
        yesterday = now - timedelta(days=1)
        users = self.env['res.users'].search([])
        service_providers = users.filtered(lambda u: u.is_service_provider)
        query_result = []
        try:
            from_date = datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day)
            to_date = datetime(year=now.year, month=now.month, day=now.day)

            for service_provider in service_providers:
                sp_merchants = users.filtered(
                    lambda u: u.is_merchant and u.invites_ids.product.service_provider_id == service_provider)
                if sp_merchants:
                    for merchant in sp_merchants:
                        sql = """
                            SELECT 
                                %s AS report_date,
                                combined_data.service_provider_id AS service_provider_id,
                                combined_data.merchant_id AS merchant_id,
                                SUM(CASE WHEN combined_data.operation = 'pull' THEN combined_data.quantity ELSE 0 END) AS pull_fees_count,
                                SUM(CASE WHEN combined_data.operation = 'pull' THEN combined_data.fees_total ELSE 0 END) AS pull_fees_total,
                                SUM(CASE WHEN combined_data.operation = 'redeem' THEN combined_data.quantity ELSE 0 END) AS redeem_fees_count,
                                SUM(CASE WHEN combined_data.operation = 'redeem' THEN combined_data.fees_total ELSE 0 END) AS redeem_fees_total
                            FROM(
                            select 'pull' as operation,
                            so.service_provider_id service_provider_id,
                            merchant.id merchant_id,
                            sum(sol.product_uom_qty) as quantity,
                            sum(sol.product_uom_qty) * %s as fees_total
                            from public.sale_order so
                            join public.sale_order_line sol on sol.order_id = so.id
                            join res_users usr on usr.id = so.service_provider_id
                            join res_partner partner on partner.id = usr.partner_id
                            join res_partner merchant on merchant.id = so.partner_id
                            where so.service_provider_id = %s and so.date_order >= %s and  so.date_order <= %s
                            and so.partner_id = %s
                            group by so.service_provider_id, merchant.id
                   
                            union all

                            select 'redeem' as operation, 
                            so.service_provider_id sp_id,
                            merchant.id m_id,
                            count(*) as quantity,
                            count(*) * %s  as fees_total
                            from public.redeem_history_prepaid hist
                                join public.product_serials ps on ps.id = hist.product_serial
                                join public.sale_order so on so.id = ps.order_id
                                join res_users usr on usr.id = so.service_provider_id
                                join res_partner partner on partner.id = usr.partner_id
                                join res_partner merchant on merchant.id = so.partner_id
                                where so.service_provider_id = %s and so.date_order >= %s and so.date_order <= %s
                                and so.partner_id = %s
                                and ps.state = '5'
                                group by so.service_provider_id, merchant.id
                                )AS combined_data
                                GROUP BY combined_data.service_provider_id,
                                   combined_data.merchant_id
                                                 """

                        self.env.cr.execute(sql, (
                            from_date,
                            service_provider.fees_value,
                            service_provider.id,
                            from_date,
                            to_date,
                            merchant.partner_id.id,
                            service_provider.redeem_fees_value,
                            service_provider.id,
                            from_date,
                            to_date,
                            merchant.partner_id.id,
                        ))
                        query_result.extend(self.env.cr.dictfetchall())
                        print(query_result)
                        if query_result:
                            self.env['daily.pull.redeem.fees.report'].sudo().create(query_result)
        except Exception as e:
            _logger.info("skarla_cron daily pull redeem fees report")
            _logger.exception(e)
            self.env.cr.rollback()
