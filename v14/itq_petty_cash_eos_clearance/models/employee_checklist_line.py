from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeChecklistLine(models.Model):
    _inherit = 'itq.employee.checklist.line'

    def action_done(self):
        if self.checklist_id.checklist_exit_type == 'petty_cash':
            pending_petty_cash_requests = self.env['petty.cash.request'].sudo().search(
                [('requested_for_id', '=', self.employee_id.id),
                 ('state', '=', 'paid'), ]).filtered(lambda r: r.remaining_amount > 0.0)
            if pending_petty_cash_requests:
                raise ValidationError(
                    _("Action can't be done because employee has paid petty cash requests not reconciled yet!!"))
            else:
                self.description = ''
                return super(EmployeeChecklistLine, self).action_done()
        else:
            return super(EmployeeChecklistLine, self).action_done()
