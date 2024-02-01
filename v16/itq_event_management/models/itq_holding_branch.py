# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqHoldingBranch(models.Model):
    _name = 'itq.holding.branch'
    _inherit = ['itq.abstract.event.lookup']
    _description = _('Branch')

    name = fields.Char(string='Branch')
    # attraction_location_ids = fields.One2many('itq.attraction.location', 'branch_id', string='Location Attraction')
    is_default_branch = fields.Boolean('Is Default Branch?', tracking=True)
    entrance_configuration_ids = fields.One2many('itq.entrance.configuration', 'branch_id', readonly=True,
                                                 domain=[('state', '=', 'active')])

    @api.constrains('is_default_branch', 'state')
    def constraint_unique_default_branch(self):
        for rec in self:
            if rec.is_default_branch and self.search_count(
                    [('state', '!=', 'archived'), ('is_default_branch', '=', True), ('id', '!=', rec.id)]):
                raise ValidationError(_('You Cannot have more than one default branch active!'))
