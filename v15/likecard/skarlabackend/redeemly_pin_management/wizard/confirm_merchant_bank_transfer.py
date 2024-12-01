from odoo import api, fields, models, _


class ConfirmMerchantBankTransfer(models.TransientModel):
    _name = 'confirm.pin.management.bank.transfer'

    bank_transfer_id = fields.Many2one('pin.management.bank.transfer.request')
    amount = fields.Float(string='Amount', related='bank_transfer_id.transferAmount')

    def confirm_approval(self):
        self.bank_transfer_id.action_approve()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
