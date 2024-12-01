# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError

import math
import logging


class AccountTax(models.Model):
    _inherit = 'account.tax'
    is_merchant = fields.Boolean(string = 'Is Merchant')
    service_provider_id = fields.Many2one('res.users', string='Service Provider',
                                          domain=[('is_service_provider', '=', True)])

    def serialize_for_api(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount_type': self.amount_type,
            'amount': self.amount,

        }
