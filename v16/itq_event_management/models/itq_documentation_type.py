# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ItqDocumentationType(models.Model):
    _name = 'itq.documentation.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Documentation Type')

    name = fields.Char(string='Documentation Type', required=True, tracking=True)
