# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReviewDepartmentSettings(models.Model):
    _name = 'review.department.settings'
    _description = "Review Department Settings"
    _rec_name = "review_department_id"

    review_department_id = fields.Many2one('hr.department', string='Department', required=True)
    allowed_units_ids = fields.Many2many('hr.department', string='allowed Units', compute='_compute_allowed_units')
    sub_review_units_ids = fields.Many2many('hr.department', string='Department Units')
    active_department = fields.Boolean(default=True, string='Active')

    @api.constrains('active_department')
    def check_active_constrains(self):
        for rec in self:
            if rec.active_department and self.search_count(
                    [('active_department', '=', True), ('id', '!=', rec.id), ]) > 0:
                raise ValidationError(_('you have to choose just one active Review Department Settings'))

    @api.onchange('review_department_id')
    def _onchange_review_department_id(self):
        self.sub_review_units_ids = False

    @api.depends('review_department_id')
    def _compute_allowed_units(self):
        for rec in self:
            rec.allowed_units_ids = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                self.review_department_id) if rec.review_department_id else False
