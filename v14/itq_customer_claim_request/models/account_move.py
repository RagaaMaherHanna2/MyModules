from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    claim_id = fields.Many2one('customer.claim.request', string='Claim', copy=False)

    def check_invoice_has_claim(self, claim_id):
        if claim_id and claim_id.state != 'cancelled':
            raise ValidationError(_('You cannot take this action on invoice has a claim request!'))

    def button_draft(self):
        for rec in self:
            rec.check_invoice_has_claim(claim_id=self.claim_id)
        return super(AccountMove, self).button_draft()

    def action_register_payment(self):
        for rec in self:
            rec.check_invoice_has_claim(claim_id=self.claim_id)
        return super(AccountMove, self).action_register_payment()

    def action_reverse(self):
        for rec in self:
            rec.check_invoice_has_claim(claim_id=self.claim_id)
        return super(AccountMove, self).action_reverse()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()
        if not self.env.context.get('from_claim_request'):
            for line in self:
                if line.move_id.claim_id:
                    line.move_id.check_invoice_has_claim(claim_id=line.move_id.claim_id)
        return res
