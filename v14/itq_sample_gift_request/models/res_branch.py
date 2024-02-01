# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class ResBranch(models.Model):
    _inherit = 'res.branch'

    apply_sample_limitation = fields.Boolean('Apply Sample/Gift limitation', default=True, )