from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    stackholder_employees_ids = fields.Many2many('hr.employee', string='Employee',
                                                 compute='_compute_stackholder_employees_ids')

    @api.depends('task_id')
    def _compute_stackholder_employees_ids(self):
        for rec in self:
            employees = self.env['hr.employee'].search([])
            if rec.task_id:
                task_stakeholders = rec.task_id.stackholder_line_ids.mapped('employee_id')
                employees = task_stakeholders | rec.task_id.user_id.employee_id
            rec.stackholder_employees_ids = employees
