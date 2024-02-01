# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProceduresReviewSettings(models.Model):
    _name = 'procedures.review.settings'
    _description = "Procedures review Settings"
    _rec_name = "review_department_id"

    review_department_id = fields.Many2one('hr.department', string='Department', required=True)
    review_allowed_users = fields.Many2many('res.users', string='Allowed review Users',
                                            compute='_compute_allowed_users')
    review_user_id = fields.Many2one('res.users', string='review User', required=True)
    allowed_review_departments = fields.Many2many('hr.department', string='Allowed Department Units',
                                                  compute='_compute_allowed_review_departments')
    review_department_units_ids = fields.Many2many('hr.department', string='Department Units')
    review_department_units = fields.Char(string='Department Units', compute='_compute_review_department_units')

    @api.constrains('review_department_units_ids', 'review_department_id')
    def _check_review_department_units(self):
        for rec in self:
            if rec.review_department_units_ids or rec.review_department_id:
                deps_to_check = rec.review_department_units_ids + rec.review_department_id
                for dep in deps_to_check:
                    if self.search([('id', '!=', rec.id),
                                    '|', ('review_department_id', '=', dep.id),
                                    ('review_department_units_ids', 'in', dep.id)]):
                        raise ValidationError(_('Department %s already has configuration!') % dep.name)

    @api.depends('review_department_units_ids')
    def _compute_review_department_units(self):
        for rec in self:
            rec.review_department_units = ', '.join(
                unit.name for unit in rec.review_department_units_ids[:10]) + (', ... ' if len(
                rec.review_department_units_ids) > 10 else '') if rec.review_department_units_ids else ''

    @api.depends('review_department_id')
    def _compute_allowed_users(self):
        for rec in self:
            review_allowed_users = []
            review_department_config = self.env['review.department.settings'].search([('active_department', '=', True)],
                                                                                     limit=1)
            if review_department_config:
                review_departments = review_department_config.review_department_id + review_department_config.sub_review_units_ids
                review_allowed_users = self.env['res.users'].search(
                    [('employee_id.current_admin_unit', 'in', review_departments.ids)])
            rec.review_allowed_users = review_allowed_users

    @api.onchange('review_department_id')
    def _onchange_review_department_id(self):
        self.review_department_units_ids = False
        self.review_user_id = False

    @api.onchange('review_user_id')
    def _onchange_review_user_id(self):
        self.review_department_units_ids = False

    @api.depends('review_user_id', 'review_department_id')
    def _compute_allowed_review_departments(self):
        for rec in self:
            sub_admin_units = []
            review_user_units_domain = [('id', 'in', [])]
            if rec.review_user_id:
                review_user_units_domain = self.env['itq.wp.access'].get_department_domain(user=rec.review_user_id)
                if rec.review_department_id:
                    sub_admin_units = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                        rec.review_department_id)
                review_user_units_domain.append(('id', 'in', sub_admin_units))
            rec.allowed_review_departments = self.env['hr.department'].search(review_user_units_domain)
