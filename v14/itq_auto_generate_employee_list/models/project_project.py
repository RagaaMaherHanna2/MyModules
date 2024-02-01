from odoo import api, fields, models
from calendar import monthrange


class Project(models.Model):
    _inherit = 'project.project'

    employee_list_id = fields.Many2one('itq.employee.list', string='Employee List')

    @api.model
    def create(self, vals_list):
        res = super(Project, self).create(vals_list)
        if self.env['ir.config_parameter'].sudo().get_param('itq_auto_generate_employee_list.for_project'):
            self.env['itq.employee.list'].create({
                'name': res.name + ' Employees List',
                'list_for': 'project',
                'project_id': res.id,
            })
        return res
