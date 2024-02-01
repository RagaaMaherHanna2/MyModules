# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqEventType(models.Model):
    _name = 'itq.event.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Event Type')

    name = fields.Char(string='Event Type', required=True, tracking=True)
    minimum_days_before_request = fields.Integer(string="Minimum Number Of Days Before Event Request", required=True,
                                                 default=60, tracking=True)

    @api.constrains('minimum_days_before_request')
    def _check_minimum_days_before_request(self):
        for record in self:
            if record.minimum_days_before_request < 0:
                raise ValidationError(_("Minimum Number Of Days Before Event Request cannot be less than 0"))
