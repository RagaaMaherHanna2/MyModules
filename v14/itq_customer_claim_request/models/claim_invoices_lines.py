# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ClaimReconciledLines(models.Model):
    _name = 'claim.invoices.lines'
    _description = 'Claim Invoices Lines'
    _rec_name = 'move_id'

    claim_id = fields.Many2one('customer.claim.request', string='Claim')
    move_id = fields.Many2one('account.move', string='NO')
    installment_line_id = fields.Many2one('invoice.installment.line', string='Instalment Line', store=True)
    line_state = fields.Selection([
        ('available', 'Available'),
        ('to_reconcile', 'To Reconcile'),
        ('partially_reconciled', 'Partially Reconciled'),
        ('reconciled', 'Reconciled'),
    ], default='available')
    checked = fields.Boolean('')
    partner_id = fields.Many2one(related='move_id.partner_id', string='Partner')
    invoice_origin = fields.Char(related='move_id.invoice_origin', string='Origin')
    invoice_date_due = fields.Date(related='move_id.invoice_date_due', string='Date')
    payment_state = fields.Selection(related='move_id.payment_state', string='Payment Status')
    amount_total_signed = fields.Monetary(related='move_id.amount_total_signed', currency_field='company_currency_id',
                                          string='Origin Amount')
    installment_company_id = fields.Many2one('installment.company', string='Installment Company')

    due_amount = fields.Monetary(currency_field='company_currency_id',
                                 string='Due Amount', store=True)
    claim_perc = fields.Float('Claim Perc', related='claim_id.claim_perc')
    company_currency_id = fields.Many2one(related='claim_id.company_currency_id')
    to_pay = fields.Monetary('To Pay Amount', currency_field='company_currency_id', compute='_compute_paid_amount')
    paid_amount = fields.Monetary('Paid Amount', currency_field='company_currency_id')

    def unlink(self):
        for rec in self:
            if rec.claim_id.state != 'draft':
                raise ValidationError(_('You cannot delete This line except draft status!'))
        return super(ClaimReconciledLines, self).unlink()

    @api.depends('claim_perc')
    def _compute_paid_amount(self):
        for rec in self:
            rec.to_pay = (rec.due_amount * rec.claim_perc) / 100 if rec.due_amount and rec.claim_perc else 0.0

    def action_to_reconcile_invoice(self):
        for rec in self:
            rec.checked = True
            rec.claim_id.reconciled_checked = True
            rec.line_state = 'to_reconcile'

