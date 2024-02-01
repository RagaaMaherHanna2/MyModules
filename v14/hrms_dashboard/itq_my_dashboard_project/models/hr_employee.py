from datetime import date

from odoo import models, api
from odoo.http import request
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def get_employee_projects(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', uid)], limit=1)
        employee_projects = employee.analytic_line_ids
        data = []
        for project_line in employee_projects:
            diff_days = 0
            end_date = date.today()
            if project_line.start_date:
                if project_line.end_date:
                    end_date = project_line.end_date
                diff_days = (end_date - project_line.start_date).days
            data.append({'label': project_line.code, 'value': diff_days})
        return data
