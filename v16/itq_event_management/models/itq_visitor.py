# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ItqVisitor(models.Model):
    _name = 'itq.visitor'
    _description = _('Visitor')

    visit_request_id = fields.Many2one('itq.visit.request', string='Visit', required=True)
    name = fields.Char(string='Name', required=True)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')