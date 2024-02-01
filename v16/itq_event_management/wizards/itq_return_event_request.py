from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReturnEventRequest(models.TransientModel):
    _name = 'itq.return.event.request'
    _description = 'Return Event Request'

    @api.model
    def get_event_request_id(self):
        active_id = self.env.context.get('active_id', False)
        return active_id

    event_request_id = fields.Many2one('itq.event.request', default=lambda self: self.get_event_request_id(),
                                       ondelete='restrict')
    return_reason = fields.Text(string="Return Reason", required=True)

    def action_of_return_event_request_wizard(self):
        self.ensure_one()
        self.event_request_id.write({
            'return_reason': self.return_reason,
        })
        return self.event_request_id.to_return()

    @api.constrains('return_reason')
    def _check_return_reason(self):
        for record in self:
            if record.return_reason.replace(' ', '') == '':
                raise ValidationError(_("Return Reason cannot be empty"))
