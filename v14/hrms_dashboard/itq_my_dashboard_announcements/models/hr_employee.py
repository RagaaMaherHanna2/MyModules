from operator import itemgetter

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def get_user_employee_details(self):
        employee = super().get_user_employee_details()

        if employee:
            employee_announcements = []
            month_start = date.today().replace(day=1)
            month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)

            this_month_approved_announcements = self.env['hr.announcement'].sudo().search(
                ['|', ('state', '=', 'approved'),
                 '&',
                 ('date_start', '>=', month_start),
                 ('date_start', '<=', month_end)])
            general_announcements = this_month_approved_announcements.filtered(lambda a: a.is_announcement)
            by_department_announcements = this_month_approved_announcements.filtered(
                lambda a: a.department_ids and employee[0]['department_id'][0] in a.department_ids.ids)

            by_job_announcements = this_month_approved_announcements.filtered(
                lambda a: a.position_ids and employee[0]['job_id'][0] in a.position_ids.ids)

            by_employee_announcements = this_month_approved_announcements.filtered(
                lambda a: a.employee_ids and employee[0]['id'] in a.employee_ids.ids)

            employee_announcements_ids = list(dict.fromkeys(general_announcements + by_department_announcements + by_job_announcements + by_employee_announcements))

            if employee_announcements_ids:
                employee_announcements = [
                    {'id': announcement.id, 'name': announcement.name, 'date_start': announcement.date_start,
                     'date_end': announcement.date_end} for
                    announcement in employee_announcements_ids]
            data = {
                'employee_announcements': employee_announcements,
                'employee_announcements_ids': list(map(itemgetter('id'), employee_announcements_ids)),
            }
            employee[0].update(data)
            return employee
        else:
            return False
