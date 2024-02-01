# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_auto_generated_list = fields.Boolean(string="Auto Generate Pay-slip Lists",
                                            config_parameter='itq_auto_generate_employee_list.is_auto_generated_list')

    for_department = fields.Boolean(config_parameter='itq_auto_generate_employee_list.for_department',
                                    string="Split Per Department")
    for_project = fields.Boolean(config_parameter='itq_auto_generate_employee_list.for_project',
                                 string="Split Per Project")

    @api.onchange('is_auto_generated_list')
    def onchange_is_auto_generated_list(self):
        if not self.is_auto_generated_list:
            self.for_department = self.for_project = False

    def fill_default_employee_list(self, old_lists, active_employees):
        old_lists = old_lists
        running_employees = active_employees.filtered(lambda e: not e.employee_list_id)
        # Archive old lists
        if old_lists:
            old_lists.filtered(lambda l: not l.list_for).active = False
        default_list = self.env.ref("itq_auto_generate_employee_list.default_employee_list")
        if default_list:
            default_list.employee_ids = running_employees.ids
            if not default_list.active:
                default_list.active = True

    def when_project_is_active(self, active_employees):
        active_projects = self.env['project.project'].search([('active', '=', True)])
        for project in active_projects:
            project_employees = active_employees.filtered(
                lambda e: e.employee_assigned_to == 'project' and e.project_id == project)
            # There are 2 cases
            # 1- project with no list ==> then create lists for
            if not project.employee_list_id:
                project_list = self.env['itq.employee.list'].sudo().create({
                    'name': project.name + ' Employees List',
                    'list_for': 'project',
                    'project_id': project.id,
                    'employee_ids': project_employees.ids,
                })
                project.employee_list_id = project_list.id
            else:
                # 2- project that where have old lists but were archived ==> reactive them
                project.employee_list_id.active = True
                project.employee_list_id.employee_ids = project_employees.ids

    def when_department_is_active(self, active_employees):
        active_departments = self.env['hr.department'].search([('active', '=', True)])
        for department in active_departments:
            department_employees = active_employees.filtered(
                lambda e: e.employee_assigned_to == 'business_unit' and e.department_id == department)

            # There are 2 cases
            # 1- department with no list ==> then create lists for
            if not department.employee_list_id:
                dep_list = self.env['itq.employee.list'].sudo().create({
                    'name': department.name + ' Employees List',
                    'list_for': 'department',
                    'department_id': department.id,
                    'employee_ids': department_employees.ids,
                })
                department.employee_list_id = dep_list.id
            else:
                # 2- department that where have old lists but were archived ==> reactive them
                department.employee_list_id.active = True
                department.employee_list_id.employee_ids = department_employees.ids

    def onchange_options(self):
        active_employees = self.env['hr.employee'].sudo().search([('contract_id.state', '=', 'open')])
        employee_lists = self.env['itq.employee.list'].sudo().search([])
        default_list = employee_lists.filtered(lambda l: l.list_for == 'default')

        # if both of 2 features are False we have to deactivate another lists and remove them employees reactivate
        # the default one
        if not self.for_project and not self.for_department:
            employee_lists.employee_ids = False
            employee_lists.filtered(lambda l: l.list_for != 'default').active = False
            self.fill_default_employee_list(old_lists=employee_lists, active_employees=active_employees)
        else:
            # if both of 2 features are true we have to deactivate the default one
            if self.for_project and self.for_department:
                default_list.active = False
                self.when_department_is_active(active_employees)
                self.when_project_is_active(active_employees)
            else:
                if self.for_department:
                    self.when_department_is_active(active_employees)
                else:
                    # when deactivate this feature archive all active lists related to all departments
                    active_departments_lists = employee_lists.filtered(lambda l: l.active and l.list_for == 'department')
                    active_departments_lists.active = False
                    active_departments_lists.employee_ids = False

                    # activate default list for employees have no lists
                    self.fill_default_employee_list(old_lists=employee_lists, active_employees=active_employees)

                if self.for_project:
                    self.when_project_is_active(active_employees)
                else:
                    # when deactivate this feature archive all active lists related to all projects
                    active_projects_lists = employee_lists.filtered(lambda l: l.active and l.list_for == 'project')
                    active_projects_lists.active = False
                    active_projects_lists.employee_ids = False

                    # activate default list for employees have no lists

                    self.fill_default_employee_list(old_lists=employee_lists, active_employees=active_employees)

    def write(self, vals):
        res = super(ResConfigSettings, self).write(vals)
        if self.is_auto_generated_list:
            self.onchange_options()
        else:
            all_lists = self.env['itq.employee.list'].sudo().search([])
            all_lists.employee_ids = False
            all_lists.filtered(lambda l: not l.list_for).active = True
            all_lists.filtered(lambda l: l.list_for).active = False
        return res
