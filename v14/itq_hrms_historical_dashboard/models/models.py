from odoo import models, _


class ItqPeriodClosureLog(models.Model):
    _inherit = 'itq.period.closure.log'

    def open_period_dashboard(self):
        return {
            'name': _('Log Dashboard'),
            'type': 'ir.actions.act_window',
            'res_model': 'itq.period.closure.log',
            'view_mode': 'dashboard',
            'target': 'current',
            'domain':  [('id', '=', self.id)],
            'context': {
                'default_current_period_log_id': 1
            }
        }


class NationalityDetailsLog(models.Model):
    _inherit = 'nationality.details.log'
    _rec_name = 'country_id'


class SponsorDetailsLog(models.Model):
    _inherit = 'sponsor.details.log'
    _rec_name = 'sponsor'


class DepartmentDetailsLog(models.Model):
    _inherit = 'department.details.log'
    _rec_name = 'department_id'
