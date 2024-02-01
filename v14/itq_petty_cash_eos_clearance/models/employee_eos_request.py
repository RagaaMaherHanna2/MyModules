from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EmployeeEosRequest(models.Model):
    _inherit = "itq.hr.employee.eos.request"

    def _get_exit_checklist(self):
        for record in self:
            res = super(EmployeeEosRequest, self)._get_exit_checklist()
            pending_petty_cash_requests = self.env['petty.cash.request'].sudo().search(
                [('requested_for_id', '=', record.employee_id.id),
                 ('state', '=', 'paid'), ]).filtered(lambda r: r.remaining_amount > 0.0)
            if pending_petty_cash_requests:
                total_remaining_amount = sum(pending_petty_cash_requests.mapped('remaining_amount'))
                petty_cash_checklist = self.env.ref('itq_petty_cash_eos_clearance.petty_cash_checklist')
                if petty_cash_checklist:
                    vals = {'termination_id': record.id,
                            'employee_id': record.employee_id.id,
                            'description': 'Total Due Petty Cash Remaining Amount = ' + str(total_remaining_amount),
                            'checklist_id': petty_cash_checklist.id}
                    self.env['itq.employee.checklist.line'].sudo().create(vals)

            return res
