from operator import itemgetter
from datetime import date, timedelta

from odoo import models, api
from odoo.http import request
from odoo.tools import float_round
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _prepare_attendance_lines(self, employee_id, start_date, last_date):
        return self.env['itq.hr.attendance.line'].sudo().search([
            ('employee_id', '=', employee_id.id), ('contract_id', 'in', employee_id.contract_ids.ids),
            ('attendance_date', '>=', start_date), ('attendance_date', '<=', last_date)]
        )

    @api.model
    def get_employee_attendance_data(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', uid)], limit=1)
        employee_projects = employee.analytic_line_ids
        data = []
        for project_line in employee_projects:
            diff_days = 0
            end_date = date.today()
            if project_line.end_date and project_line.start_date:
                if project_line.end_date:
                    end_date = project_line.end_date
                diff_days = (end_date - project_line.start_date).days
            data.append({'label': project_line.code, 'value': diff_days})
        return data

    def _get_employee_month_rest_days(self, employee_id, start_date, last_date):
        rest_days_details = []
        rest_days = self.env['itq.rest.days.assignation.line'].search(
            [('employee_id', '=', employee_id.id), ('state', '=', 'assigned'),
             ('date_from', '>=', start_date), ('date_to', '<=', last_date)])
        if rest_days:
            rest_days_details = [{'name': rd.name, 'date_from': rd.date_from, 'date_to': rd.date_to} for rd in list(set(rest_days))]
        return rest_days.ids, rest_days_details

    @staticmethod
    def _get_employee_month_work_time(employee_id, start_date, last_date):
        working_times = []
        working_times_details = []
        while start_date <= last_date:
            working_times.extend(employee_id.get_employee_work_time(start_date))
            start_date += timedelta(days=1)
        if working_times:
            working_times_details = [{'id': wt.id, 'name': wt.name} for wt in list(set(working_times))]
        return working_times_details

    @api.model
    def get_user_employee_details(self):
        employee = super().get_user_employee_details()
        if employee:
            uid = request.session.uid
            attendance_data = []
            business_trip_days = leave_early_days = leave_early_hours = late_days = late_hours = absence_days = \
                absence_hours = overtime_days = overtime_hours = rest_days_count = attended_days_count = \
                holidays_days_count = 0.0
            employee_id = self.env['hr.employee'].sudo().search(
                [('user_id', '=', uid)], limit=1)

            start_date = date.today().replace(day=1)
            last_date = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
            working_time_details = self._get_employee_month_work_time(employee_id, start_date, last_date)
            rest_day_ids, rest_day_details = self._get_employee_month_rest_days(employee_id, start_date, last_date)
            if rest_day_ids:
                rest_days_count = len(rest_day_ids)
                attendance_data.append({'label': 'Rest Days', 'value': rest_days_count})
            attendance_lines = self._prepare_attendance_lines(employee_id, start_date, last_date)
            print('attendance_lines', attendance_lines)
            if attendance_lines:
                attended_lines = attendance_lines.filtered(
                    lambda l: l.estimated_day_type == 'normal' and l.actual_day_type == 'attend')
                if attended_lines:
                    attended_days_count = len(attended_lines)
                    attendance_data.append({'label': 'Attendance', 'value': attended_days_count})
                holidays_lines = attendance_lines.filtered(lambda l: l.estimated_day_type == 'public_holiday')
                if holidays_lines:
                    holidays_days_count = len(holidays_lines)
                    attendance_data.append({'label': 'Public Holidays', 'value': holidays_days_count})

                business_trip_lines = attendance_lines.filtered(lambda l: l.estimated_day_type == 'mandate')
                if business_trip_lines:
                    business_trip_days = len(business_trip_lines)
                    attendance_data.append({'label': 'Business Trips', 'value': business_trip_days})

                leave_early_lines = attendance_lines.filtered(lambda l: l.early_out_hours > 0)
                if business_trip_lines:
                    leave_early_days = len(leave_early_lines)
                    leave_early_hours = sum(leave_early_lines.mapped('early_out_hours'))

                late_days_lines = attendance_lines.filtered(lambda l: l.late_in_hours > 0)
                if late_days_lines:
                    late_days = len(late_days_lines)
                    late_hours = sum(late_days_lines.mapped('late_in_hours'))

                absence_days_lines = attendance_lines.filtered(lambda l: l.actual_day_type == 'absence')
                if absence_days_lines:
                    absence_days = len(absence_days_lines)
                    absence_hours = sum(absence_days_lines.mapped('planned_hours'))
                    attendance_data.append({'label': 'Absence Days', 'value': absence_days})

                overtime_days_lines = attendance_lines.filtered(lambda l: l.actual_raw_overtime_hours > 0)
                if overtime_days_lines:
                    overtime_days = len(overtime_days_lines)
                    overtime_hours = sum(overtime_days_lines.mapped('actual_raw_overtime_hours'))
            print('attendance_data', attendance_data)
            data = {
                'working_time_details': working_time_details,
                'working_time_ids': list(map(itemgetter('id'), working_time_details)),
                'rest_day_details': rest_day_details,
                'employee_rest_days': rest_day_ids,
                'rest_days_count': rest_days_count,
                'business_trip_days_count': business_trip_days,
                'holidays_days_count': holidays_days_count,
                'attended_days_count': attended_days_count,
                'leave_early_days': leave_early_days,
                'leave_early_hours': leave_early_hours,
                'late_days': late_days,
                'late_hours': late_hours,
                'overtime_days': overtime_days,
                'overtime_hours': float_round(overtime_hours, precision_digits=2),
                'absence_days': absence_days,
                'absence_hours': absence_hours,
                'attendance_data': attendance_data,
            }
            employee[0].update(data)
            return employee
        else:
            return False
