# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomerClaimRequest(models.Model):
    _name = 'customer.claim.request'
    _description = 'Customer Claim Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', readonly=True)

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('submitted', 'Submitted'),
                                                        ('sent', 'Sent'),
                                                        ('partially_reconciled', 'Partially Reconciled'),
                                                        ('reconciled', 'Reconciled'),
                                                        ('rejected', 'Rejected'),
                                                        ('cancelled', 'Cancelled'),
                                                        ], default='draft', tracking=True)
    user_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, copy=False)

    submit_date = fields.Datetime('Submit Date', readonly=True, copy=False)
    sent_date = fields.Datetime('Sent Date', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                          readonly=True, )
    installment_company_id = fields.Many2one('installment.company', string='Installment Company', required=True,
                                             tracking=True,
                                             copy=False)

    payment_method_id = fields.Many2one('account.journal', required=True, domain=[('type', 'in', ['bank', 'cash'])],
                                        string='Payment Method', copy=False)
    is_date_filter = fields.Boolean(string='Date Filter')
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    rejection_reason = fields.Text('Rejection Reason')
    claim_amount = fields.Monetary('To Claim Amount', compute='_compute_claim_amount',
                                   currency_field='company_currency_id')
    paid_amount = fields.Monetary('Paid Amount', currency_field='company_currency_id')
    total_paid_amount = fields.Monetary('Request Total Paid Amount', currency_field='company_currency_id')

    claim_perc = fields.Float('Claim Perc', compute='_compute_claim_perc', default=100.0)
    reconciled_checked = fields.Boolean()

    claim_available_invoices_ids = fields.One2many('claim.invoices.lines', 'claim_id',
                                                   string='Claim Available Lines', )
    claim_reconciled_invoices_ids = fields.One2many('claim.invoices.lines', 'claim_id',
                                                    domain=[('checked', '=', True)],
                                                    string='Claim Reconciled Lines', )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('customer.claim.request.seq')
        return super(CustomerClaimRequest, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You cannot delete except draft state only!'))
        return super(CustomerClaimRequest, self).unlink()

    @api.depends('claim_reconciled_invoices_ids')
    def _compute_claim_amount(self):
        for rec in self:
            rec.claim_amount = sum(
                rec.claim_reconciled_invoices_ids.mapped('due_amount')) if rec.claim_reconciled_invoices_ids else 0.0

    @api.depends('paid_amount')
    def _compute_claim_perc(self):
        for rec in self:
            rec.claim_perc = (
                                     rec.paid_amount / rec.claim_amount) * 100 if rec.paid_amount and rec.claim_amount > 0.0 else 100

    def _validate_paid_amount(self):
        for rec in self:
            if round(rec.paid_amount, 2) > round(rec.claim_amount, 2):
                raise ValidationError(_("Paid Amount Must be <= Claim Amount"))

            if round(rec.paid_amount, 2) <= 0:
                raise ValidationError(_("Paid Amount Must be grater than 0.0!"))

    @api.onchange('is_date_filter')
    def _onchange_is_date_filter(self):
        if not self.is_date_filter:
            self.date_from = self.date_to = False

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.date_from and self.date_to:
            self._check_dates_validation()
        self._load_available_invoices(installment_company=self.installment_company_id, date_from=self.date_from,
                                      date_to=self.date_to)

    @api.onchange('installment_company_id')
    def _onchange_installment_company_id(self):
        if self.installment_company_id:
            self._load_available_invoices(installment_company=self.installment_company_id, date_from=self.date_from,
                                          date_to=self.date_to)

    @api.constrains('claim_available_invoices_ids')
    def _check_claim_available_invoices(self):
        if not self.claim_available_invoices_ids:
            validation_msg = _("This Installment Company has no Due Invoices")
            if self.date_from or self.date_to:
                validation_msg += _(' Within this period')
            raise ValidationError(validation_msg)

    def _load_available_invoices(self, installment_company, date_from=False, date_to=False):
        if self.claim_available_invoices_ids:
            self.update({'claim_available_invoices_ids': False})
        if installment_company:
            self._check_journal_request()
            domain = [
                ('invoice_id.payment_state', '!=', 'paid'),
                ('invoice_id.state', '=', 'posted'),
                ('installment_company_id', '=', installment_company.id),
                ('installment_state', '!=', 'paid'),
            ]

            move_fields = self.env['account.move'].fields_get()
            if 'invoice_type' in move_fields.keys():
                domain.extend([('invoice_id.invoice_type', '=', 'invoice')])

            if date_from and date_to:
                domain.extend(
                    [('invoice_id.invoice_date', '>=', date_from), ('invoice_id.invoice_date', '<=', date_to)])
            available_invoices = self.env['invoice.installment.line'].search(domain).filtered(
                lambda inv: inv.installment_due_amount > 0.0)
            self.update({'claim_available_invoices_ids': [(0, 0, {'move_id': line.invoice_id.id,
                                                                  'due_amount': line.installment_due_amount,
                                                                  'installment_line_id': line.id,
                                                                  'installment_company_id': line.installment_company_id.id})
                                                          for line in available_invoices]})

    def action_submit_request(self):
        self.submit_date = fields.Datetime.now()
        to_reconcile_lines = self.claim_available_invoices_ids.filtered(
            lambda l: l.line_state == 'to_reconcile')
        if not any(to_reconcile_lines):
            raise ValidationError(_('You dont have reconcile lines to submit!!'))
        to_reconcile_lines.mapped('move_id').claim_id = self.id
        self.state = 'submitted'

    def action_send_request(self):
        self.sent_date = fields.Datetime.now()
        self.state = 'sent'

    def action_cancel_request(self):
        self.state = 'cancelled'

    def action_reject_request(self):
        view_id = self.env.ref('itq_customer_claim_request.view_rejection_wizard_form').id
        return {
            'name': _('Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'rejection.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }

    def action_select_all(self):
        self.reconciled_checked = False
        if self.claim_available_invoices_ids:
            for line in self.claim_available_invoices_ids:
                line.checked = True

    def action_reconcile_request_invoices(self):
        for rec in self:
            rec._validate_paid_amount()
            for line in rec.claim_reconciled_invoices_ids.filtered(lambda inv: inv.payment_state != 'paid'):
                payment_register_vals = {'payment_date': fields.date.today(),
                                         'journal_id': rec.payment_method_id.id,
                                         'amount': line.to_pay,
                                         }
                payment_register_obj = self.env['account.payment.register'].sudo().with_context(
                    active_ids=line.move_id.id,
                    active_model='account.move').new(
                    payment_register_vals)
                payment_register_obj.sudo().with_context(from_claim_request=True)._create_payments()
                line.paid_amount = line.paid_amount + line.to_pay
                line.due_amount -= line.to_pay
                # 'installment_paid_amount': line.to_pay,
                if line.due_amount != 0.0:
                    line.line_state = 'partially_reconciled'
                    line.installment_line_id.write({'installment_state': 'partially_paid',
                                                    'installment_due_amount': line.installment_line_id.installment_due_amount - line.to_pay})
                else:
                    line.line_state = 'reconciled'
                    line.installment_line_id.write({'installment_state': 'paid',
                                                    'installment_due_amount': 0.0})

            rec.total_paid_amount = rec.total_paid_amount + rec.paid_amount
            rec.paid_amount = 0.0
            total_due_amount = sum(self.claim_reconciled_invoices_ids.mapped('due_amount'))
            if total_due_amount == 0.0:
                rec.state = 'reconciled'
            else:
                rec.state = 'partially_reconciled'

    def action_to_reconcile_invoices(self):
        for rec in self:
            rec.reconciled_checked = True
            rec.claim_available_invoices_ids.filtered(
                lambda l: l.checked and l.line_state == 'available').line_state = 'to_reconcile'

    def action_print_reconciled_inv(self):
        return self.env.ref(
            'itq_customer_claim_request.action_customer_claim_report'
        ).report_action(self)

    def _check_journal_request(self):
        domain = [('installment_company_id', '=', self.installment_company_id.id),
                  ('state', 'not in', ['cancelled', 'rejected', 'reconciled']),
                  ]

        rec_id = self.id
        if isinstance(rec_id, models.NewId):
            domain.extend([('id', '!=', rec_id.origin)])
        else:
            domain.extend([('id', '!=', rec_id)])
        if any(self.search(domain)):
            raise ValidationError(_("There's already running Request for this Installment Company"))

    def _check_dates_validation(self):
        if self.date_to < self.date_from:
            raise ValidationError(_("Date to must be after date from"))
