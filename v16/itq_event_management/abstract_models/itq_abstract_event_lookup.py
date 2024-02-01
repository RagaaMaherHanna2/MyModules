# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import re


class ItqAbstractEventLookup(models.AbstractModel):
    _name = 'itq.abstract.event.lookup'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True)
    state = fields.Selection(string='Status', required=True, tracking=True,
                             selection=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')],
                             default='draft', readonly=True)

    @api.model
    def create(self, vals):
        vals['name'] = re.sub(' +', ' ', vals['name'])
        return super(ItqAbstractEventLookup, self).create(vals)

    def write(self, vals):
        if vals and 'name' in vals.keys():
            vals['name'] = re.sub(' +', ' ', vals['name'])
        return super(ItqAbstractEventLookup, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_("You can delete record in draft state only."))
        return super(ItqAbstractEventLookup, self).unlink()

    @api.constrains('name')
    def constraint_unique_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]):
                raise ValidationError(_('You cannot duplicate {}.').format(_(self._description)))

    def set_draft(self):
        self.ensure_one()
        if self.state == 'archived':
            self.write({'state': 'draft'})
        else:
            raise ValidationError(_('State cannot be changed to draft.'))

    def activate_button(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'active'})
        else:
            raise ValidationError(_('State cannot be changed to active.'))

    def archive_button(self):
        self.ensure_one()
        if self.state == 'active':
            self.write({'state': 'archived'})
        else:
            raise ValidationError(_('State cannot be changed to archived.'))
