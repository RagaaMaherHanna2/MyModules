import calendar
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @staticmethod
    def _compute_leave_type_taken(leave_type_allocations):
        leave_type_taken = 0.0
        for allocation in leave_type_allocations:
            leave_type_taken += allocation.get_consumption_number_of_days(actual=True)
        return leave_type_taken

    @staticmethod
    def _compute_leave_type_remaining(start_date, end_date, leave_type_allocations):
        remaining_leave = 0.0
        while start_date <= end_date:
            remaining_leave = sum(map(lambda l: l.get_remaining_leaves(start_date), leave_type_allocations))
            start_date += timedelta(days=1)
        return remaining_leave

    def _get_employee_leaves_allocations(self, employee_id, start_date, end_date):
        leaves_allocation_details = []
        leave_type_allocated = leave_type_taken = leave_type_remaining = 0.0

        employee = self.browse(employee_id)
        employee_allocations = self.env['hr.leave.allocation'].search(
            [('employee_id', '=', employee_id), ('state', 'in', ['confirm', 'validate1', 'validate'])])
        employee_leave_types = employee_allocations.mapped('holiday_status_id')
        for leave_type in employee_leave_types:
            leave_type_allocations = leave_type.get_allocations(employee, date_from=start_date, date_to=end_date)
            if leave_type_allocations:
                leave_type_allocated = sum(leave_type_allocations.mapped('number_of_days'))
                leave_type_taken = self._compute_leave_type_taken(leave_type_allocations)
                leave_type_remaining = self._compute_leave_type_remaining(start_date, end_date, leave_type_allocations)

            leaves_allocation_details.append({'leave_type': leave_type.name,
                                              'leave_type_allocated_days': round(leave_type_allocated, 2),
                                              'leave_type_taken_days': round(leave_type_taken, 2),
                                              'leave_type_remaining_days': round(leave_type_remaining, 2)})
        return leaves_allocation_details

    @api.model
    def get_employee_year_allocations(self, employee_id, option_val, first_contract_date):
        years_allocation_details = []
        if option_val == 'joining':
            end_date = date.today().replace(month=12, day=31)
            if first_contract_date:
                first_contract_date = datetime.strptime(first_contract_date, '%Y-%m-%d')
                month = first_contract_date.month
                for year in range(first_contract_date.year, end_date.year + 1):
                    month_allocations = []
                    while month < 13:
                        month_start = date.today().replace(year=year, month=month, day=1)
                        month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)
                        month_allocation_details = self._get_employee_leaves_allocations(employee_id, month_start,
                                                                                         month_end)
                        month_allocations.append({
                            'month_name': calendar.month_name[month],
                            'month_allocation_details': month_allocation_details
                        })
                        month += 1
                    month = 1
                    years_allocation_details.append({'year': year,
                                                     'month_allocations': month_allocations})
        else:
            if option_val == 'p_year':
                year = date.today().year - 1
            else:
                year = date.today().year

            month_allocations = []
            month = 1
            while month < 13:
                month_start = date.today().replace(year=year, month=month, day=1)
                month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)
                month_allocation_details = self._get_employee_leaves_allocations(employee_id, month_start,
                                                                                 month_end)
                month_allocations.append({
                    'month_name': calendar.month_name[month],
                    'month_allocation_details': month_allocation_details
                })
                month += 1

            years_allocation_details.append({'year': year,
                                             'month_allocations': month_allocations})
        return years_allocation_details
