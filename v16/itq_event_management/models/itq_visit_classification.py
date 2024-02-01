# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ItqVisitClassification(models.Model):
    _name = 'itq.visit.classification'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Visit Classification')

    name = fields.Char(string='Visit Classification', required=True, tracking=True)
