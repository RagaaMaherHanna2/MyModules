from odoo import api, fields, models
from calendar import monthrange


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if self.env['ir.config_parameter'].sudo().get_param(
                'itq_auto_generate_employee_list.is_auto_generated_list'):
            if any(val in vals for val in
                   ['state', 'employee_assigned_to', 'assigned_to_line_ids',
                    'contract_id']):
                for rec in self:
                    rec.reflect_on_employee_list()

        return res

    def reflect_on_employee_list(self):
        all_employee_lists = self.env['itq.employee.list'].search([])
        default_list = self.env.ref("itq_auto_generate_employee_list.default_employee_list")

        if self.employee_list_id and self.state == 'inactive':
            self.employee_list_id = False

        elif self.contract_id.state == 'open':
            if self.employee_assigned_to == 'business_unit':
                if self.env['ir.config_parameter'].sudo().get_param('itq_auto_generate_employee_list.for_department'):
                    department_list = all_employee_lists.filtered(lambda el: el.department_id == self.department_id)
                    if department_list:
                        if self.id not in department_list.employee_ids.ids:
                            self.employee_list_id = department_list.id
                else:
                    if default_list:
                        self.employee_list_id = default_list.id
            else:
                if self.env['ir.config_parameter'].sudo().get_param('itq_auto_generate_employee_list.for_project'):
                    project_list = all_employee_lists.filtered(lambda el: el.project_id == self.project_id)
                    if project_list:
                        if self.id not in project_list.employee_ids.ids:
                            self.employee_list_id = project_list.id
                else:
                    if default_list:
                        self.employee_list_id = default_list.id
