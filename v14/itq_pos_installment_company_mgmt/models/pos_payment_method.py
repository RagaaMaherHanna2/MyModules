# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import api, fields, models, _


class PoSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_installment_method = fields.Boolean('Is Installment Company?')
    installment_company_id = fields.Many2one('installment.company', string='Installment Company')

