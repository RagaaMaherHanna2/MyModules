# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InvoiceInstallmentLine(models.Model):
    _name = 'invoice.installment.line'
    _description = 'Invoice Installment Line'
    _rec_name = 'installment_company_id'

    invoice_id = fields.Many2one('account.move', string='Invoice', )
    pos_order_id = fields.Many2one('pos.order', string='Order', )

    installment_company_id = fields.Many2one('installment.company', string='Installment Company', required=True)
    installment_amount = fields.Float('Installment Amount')
    installment_due_amount = fields.Float('Installment Due Amount', readonly=True, store=True)
    # installment_paid_amount = fields.Float('Installment Paid Amount', readonly=1)
    installment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ], default='not_paid', readonly=1)

    def unlink(self):
        for rec in self:
            if rec.invoice_id.state != 'draft':
                raise ValidationError(_("Cannot delete installment of a posted invoice"))
        return super(InvoiceInstallmentLine, self).unlink()

    @api.constrains('installment_amount')
    def _validate_amounts(self):
        for rec in self:
            if round(rec.installment_amount, 2) <= 0.0:
                raise ValidationError(_("Installment Amount Must be grater than 0.0!"))

    @api.onchange('installment_amount')
    def _onchange_installment_amount(self):
        if self.installment_amount and self.installment_state == 'not_paid':
            self.installment_due_amount = self.installment_amount
