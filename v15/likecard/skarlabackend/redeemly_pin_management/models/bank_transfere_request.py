from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
_logger = logging.getLogger(__name__)


class BankTransferModel(models.Model):
    _name = 'pin.management.bank.transfer.request'
    _inherit = ['mail.thread']
    _description = 'Merchant Bank Transfer Request'

    bank = fields.Many2one('res.partner.bank')
    bankName = fields.Char(related='bank.bank_id.name')
    senderAccount = fields.Char(related='bank.acc_number')
    toBank = fields.Many2one('res.partner.bank')
    transferAmount = fields.Float(string='Transfer Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    note = fields.Char(string='Note')
    bankTransferImage = fields.Binary(string='Bank Transfer Attachment')
    partner_id = fields.Many2one('res.partner', string='Merchant')
    bankTransferImageURL = fields.Char(string='Bank Transfer Attachment URL', compute="compute_image_url")
    sequence = fields.Char(string="Order Sequence")
    type=fields.Selection(selection=[
        ('deposit', 'deposit'),
        ('credit', 'credit'),
        ('invoice_payment', 'invoice payment')
    ], default='deposit')
    invoice_id = fields.Many2one('account.move', domain=[('move_type', '=', 'out_invoice')])

    def get_public_url(self):
        self.ensure_one()
        self.compute_image_url()
        url = self.bankTransferImageURL
        base_url = self.env['ir.config_parameter'].sudo().get_param('s3.obj_url')
        return url.replace(base_url, "/exposed/download_bank_transfer_image?file_hash=") if url else False

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'id': self.id,
            'image': self.get_public_url(),
            'merchant': {
                'id': self.partner_id.id,
                'name': self.partner_id.name
            },
            'bank_name': self.bankName,
            'to_bank': self.toBank.bank_id.name,
            'transfer_amount': self.transferAmount,
            'state': self.state,
            'note': self.note,
            'type': self.type,
            'date': datetime.strftime(self.create_date, DATETIME_FORMAT) if self.create_date else None
        }

    @api.model
    def create(self, vals):
        vals["sequence"] = self.env["ir.sequence"].next_by_code("bank.transfer.request")
        return super(BankTransferModel, self).create(vals)

    @api.onchange("bankTransferImage")
    def compute_image_url(self):
        for rec in self:
            attachment = self.env['ir.attachment'].search(
                [("res_model", "=", "pin.management.bank.transfer.request"), ('res_id', '=', rec.id),
                 ('res_field', '=', 'bankTransferImage')])
            if attachment:
                rec.bankTransferImageURL = attachment[0].url
            else:
                rec.bankTransferImageURL = ""

    def show_confirmation_wizard_before_approve(self):
        wizard = self.env['confirm.pin.management.bank.transfer'].create({'bank_transfer_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.pin.management.bank.transfer',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref(
                'redeemly_pin_management.confirm_merchant_bank_transfer_view').id,
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_approve(self):
        # if not self.bankTransferImage:
        #     raise UserError("Image Transfer Image Required")
        # if not self.bank:
        #     raise UserError("Please Choose From Bank Account Before")
        if self.type == 'deposit':
            self.deposit(self.transferAmount, self.partner_id, self.sequence)
        elif self.type == 'credit':
            self.credit(self.transferAmount, self.partner_id, self.sequence)
        else:
            self.pay_invoice()
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def deposit(self, amount, partner, reference):
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
        debit_account_id = self.env.ref('redeemly_pin_management.account_wallet_debit')
        credit_account_id = self.env.ref('redeemly_pin_management.account_wallet_credit')
        credit_line = {
            'account_id': credit_account_id.id,
            'credit': amount,
            'debit': 0,
            'name': "Deposit Wallet Using Bank Transfer %s" % reference,
            'currency_id': self.toBank.partner_id.user_ids.sp_currency.id,
            'partner_id': partner.id
        }
        debit_line = {
            'account_id': debit_account_id.id,
            'credit': 0,
            'debit': amount,
            'name': "Deposit Wallet Using Bank Transfer %s" % reference,
            'currency_id': self.toBank.partner_id.user_ids.sp_currency.id,
            'partner_id': partner.id
        }
        journal = self.env['account.move'].sudo().create({
            'name': str(datetime.now()) + "-Deposit-" + partner.user_ids.reference,
            'move_type': 'entry',
            'date': fields.date.today(),
            'line_ids': [(0, 0, credit_line), (0, 0, debit_line)],
            'journal_id': journal_id.id
        })
        journal.action_post()
        partner.balance = partner.balance + amount

    def credit(self, amount, partner, reference):
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
        debit_account_id = self.env.ref('redeemly_pin_management.account_wallet_debit')
        credit_account_id = self.env.ref('redeemly_pin_management.account_wallet_credit')
        credit_line = {
            'account_id': debit_account_id.id,
            'credit': amount,
            'debit': 0,
            'currency_id': self.bank.partner_id.user_ids.sp_currency.id,
            'partner_id': partner.id
        }
        debit_line = {
            'account_id': credit_account_id.id,
            'credit': 0,
            'debit': amount,
            'name': "Credit Wallet Using Bank Transfer %s"%reference,
            'currency_id': self.bank.partner_id.user_ids.sp_currency.id,
            'partner_id': partner.id
        }
        journal = self.env['account.move'].sudo().create({
            'name': str(datetime.now()) + "-Credit-" + partner.user_ids.reference,
            'move_type': 'entry',
            'date': fields.date.today(),
            'line_ids': [(0, 0, credit_line), (0, 0, debit_line)],
            'journal_id': journal_id.id
        })
        journal.action_post()
        partner.balance = partner.balance - amount

    def pay_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError("Invalid Invoice ID")
        if self.invoice_id.amount_total != self.transferAmount:
            raise UserError("Transferred amount should be equal to invoice amount %s"%(self.invoice_id.amount_total))

        journal_id = self.env['account.journal'].sudo().search([('name', '=', 'Bank')])
        pay = self.env['account.payment.register'].sudo().with_context(active_model='account.move',
                                                                                           active_ids=self.invoice_id.ids). \
            create({
            'payment_date': self.create_date,
            'amount': abs(self.transferAmount),
            'currency_id': self.env.company.currency_id.id,
            'journal_id': journal_id.id,
        }). \
            _create_payments()



class PartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_type = fields.Char(string='Account Type')
    account_class = fields.Char(string='Account Class')
    iban = fields.Char(string='IBAN')
    adib_swift_code = fields.Char(string='ADIB Swift Code')

    _sql_constraints = [
        ('unique_number', 'CHECK(1=1)', 'Account Number must be unique'),
    ]
