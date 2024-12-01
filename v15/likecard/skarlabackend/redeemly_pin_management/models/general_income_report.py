import base64

from odoo import models, fields, api, _
import logging


_logger = logging.getLogger(__name__)


class GeneralIncomeReport(models.Model):
    _name = 'general.income.report'

    operation = fields.Selection([('pull', 'Pull'), ('redeem', 'Redeem')])
    report_date = fields.Datetime()
    service_provider_id = fields.Many2one('res.users', string='Service Provider', index=True)
    merchant_id = fields.Many2one('res.partner', string='Merchant', index=True)
    pull_fees_count = fields.Float()
    pull_fees_total = fields.Float()
    redeem_fees_count = fields.Float()
    redeem_fees_total = fields.Float()

