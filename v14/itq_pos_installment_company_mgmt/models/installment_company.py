# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class InstallmentCompany(models.Model):
    _name = 'installment.company'
    _description = 'Installment Company'

    name = fields.Char(required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    total_installments_amount = fields.Monetary(compute='_compute_total_installments_amount')

    def _compute_total_installments_amount(self):
        for rec in self:
            total_installments_amount = sum(
                self.env['invoice.installment.line'].search([('installment_company_id', '=', rec.id),
                                                             ('installment_state', '!=', 'paid')]).mapped('installment_due_amount'))
            rec.total_installments_amount = total_installments_amount
