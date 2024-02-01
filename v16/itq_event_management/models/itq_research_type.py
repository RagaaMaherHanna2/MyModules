# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ItqResearchType(models.Model):
    _name = 'itq.research.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Research Type')

    name = fields.Char(string='Research Type', required=True, tracking=True)