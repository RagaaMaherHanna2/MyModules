from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError


class SampleRejectionWizard(models.TransientModel):
    _name = 'sample.rejection.wizard'
    _description = 'Sample Rejection Wizard'

    name = fields.Char()
    rejection_reason = fields.Text(required=True)

    def reject_action(self):
        self.ensure_one()
        model = self.env.context.get('active_model')
        request = self.env[model].browse(self.env.context.get('active_id'))
        if request.state == 'confirmed':
            request.write({
                'rejection_reason': self.rejection_reason,
                'state': 'rejected'
            })
