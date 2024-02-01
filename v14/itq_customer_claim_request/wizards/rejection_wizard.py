from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError


class RejectionWizard(models.TransientModel):
    _name = 'rejection.wizard'
    _description = 'Rejection Wizard'

    name = fields.Char()
    rejection_reason = fields.Text(required=True)

    def reject_action(self):
        self.ensure_one()
        model = self.env.context.get('active_model')
        request = self.env[model].browse(self.env.context.get('active_id'))
        request.write({
            'rejection_reason': self.rejection_reason,
            'state': 'rejected'
        })
