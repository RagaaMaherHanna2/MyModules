# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    installment_paying = fields.Boolean('Is Installment Paying?', copy=False)
    installment_line_ids = fields.One2many('invoice.installment.line', 'invoice_id', 'Installments')
    total_installments_amount = fields.Float(string='Installments Amounts',
                                             compute='_compute_invoice_installment_amount')

    @api.depends('installment_line_ids')
    def _compute_invoice_installment_amount(self):
        for rec in self:
            rec.total_installments_amount = sum(
                rec.installment_line_ids.mapped('installment_amount')) if rec.installment_line_ids else 0.0

    @api.constrains('installment_line_ids', 'total_installments_amount', 'amount_total')
    def _check_validate_installments_amount(self):
        for rec in self:
            if rec.installment_line_ids:
                if rec.total_installments_amount > rec.amount_total:
                    raise ValidationError(_("Total Installments  Amount Must be <= Total Invoice Amount"))

    @api.constrains('installment_paying', 'installment_line_ids')
    def _check_installments_lines(self):
        for rec in self:
            if rec.installment_paying and not rec.installment_line_ids:
                raise ValidationError(_("Installment invoice must have instalment lines"))
