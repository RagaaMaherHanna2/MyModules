# -*- coding: utf-8 -*-
from odoo import fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    sample_id = fields.Many2one('sample.gift.request', string='Sample')
