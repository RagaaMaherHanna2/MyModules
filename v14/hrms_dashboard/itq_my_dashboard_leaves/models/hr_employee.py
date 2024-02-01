import calendar
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_leaves(self, employee_id, start_date, end_date):
        domain = [('state', 'in', ['confirm', 'validate1']),
                  ('employee_id', '=', employee_id)]
        if start_date and end_date:
            domain.extend([('request_date_from', '>=', start_date), ('request_date_to', '<=', end_date)])
        return self.env['hr.leave'].sudo().search(domain)

    def _get_employee_leaves_allocations(self, employee_id, start_date, end_date):
        leaves_allocation_details = []
        employee_allocations = self.env['hr.leave.allocation'].search(
            [('employee_id', '=', employee_id), ('state', 'in', ['confirm', 'validate1', 'validate'])])
        employee_leave_types = employee_allocations.mapped('holiday_status_id')
        for leave_type in employee_leave_types:
            leave_type_allocated_days = sum(employee_allocations.filtered(
                lambda allocation: allocation.holiday_status_id == leave_type).mapped('number_of_days'))
            leave_type_taken_days = sum(self._get_leaves(employee_id, start_date, end_date).filtered(
                lambda leave: leave.holiday_status_id == leave_type).mapped('number_of_days'))
            leave_type_remaining_days = leave_type_allocated_days - leave_type_taken_days
            leaves_allocation_details.append({'leave_type': leave_type.name,
                                              'leave_type_allocated_days': round(leave_type_allocated_days, 2),
                                              'leave_type_taken_days': round(leave_type_taken_days, 2),
                                              'leave_type_remaining_days': round(leave_type_remaining_days, 2),
                                              })
        return leaves_allocation_details
    #
    # # TODO remove below fun
    # @api.model
    # def get_employee_year_allocations(self, employee_id, option_val, first_contract_date):
    #     years_allocation_details = []
    #     if option_val == 'joining':
    #         end_date = date.today().replace(month=12, day=31)
    #         if first_contract_date:
    #             first_contract_date = datetime.strptime(first_contract_date, '%Y-%m-%d')
    #             month = first_contract_date.month
    #             for year in range(first_contract_date.year, end_date.year + 1):
    #                 month_allocations = []
    #                 while month < 13:
    #                     month_start = date.today().replace(year=year, month=month, day=1)
    #                     month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)
    #                     month_allocation_details = self._get_employee_leaves_allocations(employee_id, month_start,
    #                                                                                      month_end)
    #                     month_allocations.append({
    #                         'month_name': calendar.month_name[month],
    #                         'month_allocation_details': month_allocation_details
    #                     })
    #                     month += 1
    #
    #                 years_allocation_details.append({'year': year,
    #                                                  'month_allocations': month_allocations})
    #     else:
    #         if option_val == 'p_year':
    #             year = date.today().year - 1
    #         else:
    #             year = date.today().year
    #
    #         month_allocations = []
    #         month = 1
    #         while month < 13:
    #             month_start = date.today().replace(year=year, month=month, day=1)
    #             month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)
    #             month_allocation_details = self._get_employee_leaves_allocations(employee_id, month_start,
    #                                                                              month_end)
    #             month_allocations.append({
    #                 'month_name': calendar.month_name[month],
    #                 'month_allocation_details': month_allocation_details
    #             })
    #             month += 1
    #
    #         years_allocation_details.append({'year': year,
    #                                          'month_allocations': month_allocations})
    #
    #     return years_allocation_details

    @api.model
    def get_user_employee_details(self):
        employee = super().get_user_employee_details()
        if employee:
            employee_id = employee[0]['id']
            leaves_to_approve_count = leaves_today_count = leaves_this_month_count = 0.0
            leaves_to_approve = self._get_leaves(employee_id, start_date=False, end_date=False).ids
            if leaves_to_approve:
                leaves_to_approve_count = len(leaves_to_approve)

            today = datetime.strftime(datetime.today(), '%Y-%m-%d')
            leaves_today = self._get_leaves(employee_id, start_date=today, end_date=today).ids
            if leaves_today:
                leaves_today_count = len(leaves_today)

            start_date = date.today().replace(day=1)
            end_date = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
            leaves_this_month = self._get_leaves(employee_id, start_date=start_date, end_date=end_date).ids
            if leaves_this_month:
                leaves_this_month_count = len(leaves_this_month)

            start_date = employee[0]['first_contract_date']
            end_date = date.today().replace(month=12, day=31)
            leaves_allocation_details = self._get_employee_leaves_allocations(employee_id, start_date, end_date)

            data = {
                'leaves_to_approve': leaves_to_approve,
                'leaves_to_approve_count': leaves_to_approve_count,
                'leaves_today': leaves_today,
                'leaves_today_count': leaves_today_count,
                'leaves_this_month': leaves_this_month,
                'leaves_this_month_count': leaves_this_month_count,
                'leaves_allocation_details': leaves_allocation_details,
                # 'year_allocation_details': year_allocation_details,
            }
            employee[0].update(data)
            return employee
        else:
            return False
