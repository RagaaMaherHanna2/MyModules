# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProceduresConfirmSettings(models.Model):
    _name = 'procedures.confirm.settings'
    _description = "Procedures confirm Settings"
    _rec_name = "confirm_department_id"

    _sql_constraints = [
        ("unique_confirm_department_id", "UNIQUE (confirm_department_id)",
         _("This department already has configuration record."))
    ]

    confirm_department_id = fields.Many2one('hr.department', string='Department', required=True)
    confirm_allowed_users = fields.Many2many('res.users', string='Allowed Confirm Users',
                                             compute='_compute_allowed_users')
    confirm_user_id = fields.Many2one('res.users', string='Confirm User', required=True)
    allowed_confirm_departments = fields.Many2many('hr.department', string='Allowed Department Units',
                                                   compute='_compute_allowed_confirm_departments')
    confirm_department_units_ids = fields.Many2many('hr.department', string='Department Units', required=True)
    confirm_department_units = fields.Char(string='Department Units', compute='_compute_confirm_department_units')

    @api.constrains('confirm_department_units_ids', 'confirm_department_id')
    def _check_confirm_department_units(self):
        for rec in self:
            if rec.confirm_department_units_ids or rec.confirm_department_id:
                deps_to_check = rec.confirm_department_units_ids + rec.confirm_department_id
                for dep in deps_to_check:
                    if self.search_count([('id', '!=', rec.id),
                                          '|', ('confirm_department_id', '=', dep.id),
                                          ('confirm_department_units_ids', 'in', dep.id)]) > 0:
                        raise ValidationError(_('Department %s already has configuration!') % dep.name)

    @api.depends('confirm_department_units_ids')
    def _compute_confirm_department_units(self):
        for rec in self:
            rec.confirm_department_units = ', '.join(
                unit.name for unit in rec.confirm_department_units_ids[:10]) + (', ... ' if len(
                rec.confirm_department_units_ids) > 10 else '') if rec.confirm_department_units_ids else ''

    @api.depends('confirm_department_id')
    def _compute_allowed_users(self):
        for rec in self:
            confirm_allowed_users = False
            if rec.confirm_department_id:
                sub_admin_units_ids = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                    rec.confirm_department_id)
                confirm_allowed_users = self.env['res.users'].search(
                    ['|', ('employee_id.current_admin_unit', '=', rec.confirm_department_id.id),
                     ('employee_id.current_admin_unit', 'in', sub_admin_units_ids)])

            rec.confirm_allowed_users = confirm_allowed_users

    @api.onchange('confirm_department_id')
    def _onchange_confirm_department_id(self):
        self.confirm_department_units_ids = False
        self.confirm_user_id = False

    @api.onchange('confirm_user_id')
    def _onchange_confirm_user_id(self):
        self.confirm_department_units_ids = False

    @api.depends('confirm_department_id', 'confirm_user_id')
    def _compute_allowed_confirm_departments(self):
        for rec in self:
            sub_admin_units = []
            confirm_user_units_domain = [('id', 'in', [])]
            if rec.confirm_department_id:
                sub_admin_units = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                    rec.confirm_department_id)

            if rec.confirm_user_id:
                confirm_user_units_domain = self.env['itq.wp.access'].get_department_domain(user=rec.confirm_user_id)
                confirm_user_units_domain = (confirm_user_units_domain and ['&'] or []) + confirm_user_units_domain + [
                    ('id', 'in', sub_admin_units)]
            rec.allowed_confirm_departments = self.env['hr.department'].search(confirm_user_units_domain)
