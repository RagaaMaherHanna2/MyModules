from odoo import api, fields, models, _
from datetime import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    is_project_variable_wage = fields.Boolean(string="Apply Project Variable Wage")
    project_variable_ids = fields.One2many('project.variable', 'contract_id', string="Variable Salary", tracking=True)
    selected_projects_ids = fields.Many2many('project.project', compute='_compute_selected_projects_ids')

    @api.depends('project_variable_ids')
    def _compute_selected_projects_ids(self):
        for rec in self:
            selected_projects = []
            if rec.project_variable_ids:
                selected_projects = rec.project_variable_ids.mapped('project_id')
            rec.selected_projects_ids = selected_projects

