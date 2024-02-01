# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ItqOrganizationType(models.Model):
    _name = 'itq.organization.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Organization Type')

    name = fields.Char(string='Organization Type', required=True, tracking=True)