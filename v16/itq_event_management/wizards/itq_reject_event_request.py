from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RejectEventRequest(models.TransientModel):
    _name = 'itq.reject.event.request'
    _description = 'Reject Event Request'

    @api.model
    def get_event_request_id(self):
        active_id = self.env.context.get('active_id', False)
        return active_id

    event_request_id = fields.Many2one('itq.event.request', default=lambda self: self.get_event_request_id(),
                                       ondelete='restrict')
    rejection_reason = fields.Text(string="Reject Reason", required=True)

    def action_of_reject_event_request_wizard(self):
        self.ensure_one()
        self.event_request_id.write({
            'rejection_reason': self.rejection_reason,
        })
        return self.event_request_id.to_reject()

    @api.constrains('rejection_reason')
    def _check_rejection_reason(self):
        for record in self:
            if record.rejection_reason.replace(' ', '') == '':
                raise ValidationError(_("Reject Reason cannot be empty"))
