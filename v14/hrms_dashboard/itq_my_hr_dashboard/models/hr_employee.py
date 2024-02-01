from operator import itemgetter

from odoo import models, fields, api
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_expiring_docs(self, employee_id):
        first_day = date.today()
        last_day = (date.today() + relativedelta(months=2)) - timedelta(1)
        ex_docs = self.env['itq.document'].search([('employee_id', '=', employee_id),
                                                   ('expiry_date', '>=', first_day),
                                                   ('expiry_date', '<=', last_day)])
        ex_docs_details = []
        if ex_docs:
            ex_docs_details = [
                {'id': doc.id, 'name': doc.name, 'date_start': doc.date_start,
                 'date_end': doc.date_end} for
                doc in ex_docs]
        return ex_docs_details

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read(
            [('user_id', '=', uid)], limit=1)

        date_end = grade = degree = experience = first_contract_date = False
        remaining_days = 0
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')
        if employee:
            print(employee[0]['name'])
            expiring_docs = self._get_expiring_docs(employee[0]['id'])
            if employee[0]['contract_id']:
                employee_contract = self.env['hr.contract'].sudo().browse(employee[0]['contract_id'][0])
                grade = employee_contract.salary_grade_id
                if grade:
                    grade = grade.name
                degree = employee_contract.salary_degree_id
                if degree:
                    degree = degree.name
                if employee_contract.date_end:
                    date_end = datetime.strftime(employee_contract.date_end, '%Y-%m-%d')

                def days_between(d1, d2):
                    d1 = datetime.strptime(d1, "%Y-%m-%d")
                    d2 = datetime.strptime(d2, "%Y-%m-%d")
                    return abs((d2 - d1).days)

                if date_end:
                    remaining_days = days_between(date_end, today)

            if employee[0]['first_contract_date']:
                first_contract_date = employee[0]['first_contract_date']
                diff = relativedelta(datetime.today(),
                                     employee[0]['first_contract_date'])
                years = diff.years
                months = diff.months
                days = diff.days
                experience = '{} years {} months {} days'.format(years, months,
                                                                 days)
            employee_assigned_to = dict(
                self.env['hr.employee'].fields_get(['employee_assigned_to'])['employee_assigned_to']['selection'])

            ks_my_default_dashboard_board = self.env.ref('ks_dashboard_ninja.ks_my_default_dashboard_board').id
            data = {
                'expiring_docs': expiring_docs,
                'expiring_docs_ids':list(map(itemgetter('id'), expiring_docs)),
                'experience': experience,
                'grade': grade,
                'degree': degree,
                'date_end': date_end,
                'remaining_days': remaining_days,
                'first_contract_date': first_contract_date,
                'employee_assigned_to': employee_assigned_to[employee[0]['employee_assigned_to']],
                'ks_my_default_dashboard_board': ks_my_default_dashboard_board,
                'today': date.today(),
            }
            employee[0].update(data)
            return employee
        else:
            return False

    @api.model
    def get_employee_jobs(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', uid)], limit=1)
        employee_jobs = employee.job_line_ids
        data = []
        for job_line in employee_jobs:
            diff_days = 0
            end_date = date.today()
            if job_line.start_date:
                if job_line.end_date:
                    end_date = job_line.end_date
                diff_days = relativedelta(end_date, job_line.start_date).days
            data.append({'label': job_line.job_id.name, 'value': diff_days})
        return data

    @api.model
    def get_employee_departments(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', uid)], limit=1)
        employee_departments = employee.department_line_ids
        data = []
        for dep_line in employee_departments:
            diff_days = 0
            end_date = date.today()
            if dep_line.start_date:
                if dep_line.end_date:
                    end_date = dep_line.end_date
                diff_days = (end_date - dep_line.start_date).days
            data.append({'label': dep_line.department_id.name, 'value': diff_days})
        return data
