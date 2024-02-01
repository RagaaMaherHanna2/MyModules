# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CommitteeMember(models.Model):
    _name = 'committee.member'
    _description = "Committee Member"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', 'Name', required=True)
    member_class = fields.Selection([('member', 'Member'),
                                     ('manager', 'Manager')], string='Classification', required=True)
    identification_id = fields.Char(string="Identification ID", related='employee_id.identification_id', readonly=True)
    committee_id = fields.Many2one('documentation.committee', string='Committee')
    active_member = fields.Boolean(default=True)

    @api.constrains('id', 'member_class', 'committee_id', 'employee_id', 'active_member')
    def check_member_class(self):
        for rec in self:
            if rec.member_class == 'manager' and rec.active_member and any(self.search([('id', '!=', rec.id),
                                                                                        (
                                                                                                'member_class', '=',
                                                                                                'manager'),
                                                                                        ('active_member', '=', True),
                                                                                        ('committee_id', '=',
                                                                                         rec.committee_id.id)])):
                raise ValidationError(_('Committee Must have one Active manager'))
            if self.search([('id', '!=', rec.id),
                            ('employee_id', '=', rec.employee_id.id),
                            ('committee_id', '=', rec.committee_id.id)]):
                raise ValidationError(
                    _('This Member (%s) is registered for this committee before') % rec.employee_id.name)
