from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = 'project.task'

    stackholder_line_ids = fields.One2many('task.stackholder.line', 'task_id', string='Task Stackholders')

    stackholder_employees_ids = fields.Many2many('hr.employee', string='Employees',
                                                 compute='_compute_stackholder_employees_ids')

    @api.depends('project_id.stakeholder_ids')
    def _compute_stackholder_employees_ids(self):
        for rec in self:
            employees = False
            if rec.project_id.stakeholder_ids:
                project_stakeholders = rec.project_id.stakeholder_ids.filtered(
                    lambda s: s.stakeholder_type == 'internal').mapped('employee_id')
                employees = project_stakeholders.mapped('employee_ids')
            rec.stackholder_employees_ids = employees
