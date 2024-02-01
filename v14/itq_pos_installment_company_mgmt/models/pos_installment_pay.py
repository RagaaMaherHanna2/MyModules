# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError
import psycopg2
from odoo.http import request
from functools import partial
from odoo.tools import float_round
import logging
from collections import defaultdict
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class POSConfigInherit(models.Model):
    _inherit = 'pos.config'

    allow_installment_payment = fields.Boolean('Allow Installment Payment?')
    payment_journal_id = fields.Many2one('account.journal', domain=[('type', 'in', ['bank', 'cash'])],
                                         string='Installment Payment Journal', copy=False)


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    def _default_session(self):
        return self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)

    is_installment = fields.Boolean('Is Installment Payment')

    def write(self, vals):
        for order in self:
            if order.name == '/' and order.is_installment:
                vals['name'] = order.config_id.sequence_id._next()
        return super(PosOrderInherit, self).write(vals)

    def action_pos_order_paid(self):
        self.ensure_one()
        if not self.is_installment:
            return super(PosOrderInherit, self).action_pos_order_paid()
        else:
            if not self.config_id.cash_rounding:
                total = self.amount_total
            else:
                total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding,
                                    rounding_method=self.config_id.rounding_method.rounding_method)
            if self._is_pos_order_paid():
                self.write({'state': 'paid'})
                if self.picking_ids:
                    return True
                else:
                    return self._create_order_picking()
            else:
                if not self.picking_ids:
                    return self._create_order_picking()
                else:
                    return False

    def _prepare_installments_lines(self, payment):
        return {
            'installment_company_id': payment.payment_method_id.installment_company_id.id,
            'pos_order_id': self.id,
            'installment_amount': payment.amount,
            'installment_due_amount': payment.amount,
        }

    def _prepare_invoice_vals(self):
        vals = super(PosOrderInherit, self)._prepare_invoice_vals()
        if vals:
            vals.update({'installment_line_ids': [(0, None, self._prepare_installments_lines(payment)) for payment in
                                                  self.payment_ids.filtered(
                                                      lambda p: p.payment_method_id.is_installment_method)],
                         'installment_paying': True})
        return vals

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrderInherit, self)._order_fields(ui_order)
        if 'is_installment' in ui_order:
            res['is_installment'] = ui_order.get('is_installment', False)
        return res

    def is_installment_returned_order(self, returned_order):
        return self.env['pos.order'].browse(returned_order).is_installment

    @staticmethod
    def get_order_cash_paid(returned_order):
        return sum(returned_order.payment_ids.filtered(
            lambda p: p.payment_method_id.is_cash_count and not p.payment_method_id.is_installment_method).mapped(
            'amount'))

    @api.model
    def _process_order(self, order, draft, existing_order):
        print('im in itq_pos_installment_company_mgmt')
        is_paying_installment = order['data'].get('is_installment')
        returned_order = self.env['pos.order'].browse(int(order['data'].get('return_order_ref')))
        # handle installment paying cycle
        if is_paying_installment:
            order = order['data']
            pos_session = self.env['pos.session'].browse(order['pos_session_id'])
            if pos_session.state == 'closing_control' or pos_session.state == 'closed':
                order['pos_session_id'] = self._get_valid_session(order).id

            if not existing_order:
                pos_order = self.create(self._order_fields(order))
            else:
                pos_order = existing_order
                pos_order.lines.unlink()
                order['user_id'] = pos_order.user_id.id
                pos_order.write(self._order_fields(order))

            pos_order = pos_order.with_company(pos_order.company_id)
            self = self.with_company(pos_order.company_id)
            self._process_payment_lines(order, pos_order, pos_session, draft)

            if not draft:
                try:
                    pos_order.action_pos_order_paid()
                except psycopg2.DatabaseError:
                    # do not hide transactional errors, the order(s) won't be saved!
                    raise
                except Exception as e:
                    _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
                pos_order._create_order_picking()

            if order.get('to_invoice', False):
                pos_order.action_pos_order_invoice()
                invoice = pos_order.account_move
                for payment in pos_order.payment_ids.filtered(lambda p: not p.payment_method_id.is_installment_method):
                    journal = pos_order.config_id.payment_journal_id
                    # try:
                    payment_register_vals = {'payment_date': fields.date.today(),
                                             'journal_id': journal.id,
                                             'amount': payment.amount,
                                             'payment_difference_handling': 'open',
                                             }
                    payment_register_obj = self.env['account.payment.register'].sudo().with_context(
                        active_ids=invoice.id,
                        active_model='account.move').new(
                        payment_register_vals)
                    payments = payment_register_obj.sudo().with_context(from_claim_request=True)._create_payments()
                    print(payments)
                    # except Exception as e:
                    #     _logger.error('Could not create payment %s', tools.ustr(e))

            return pos_order.id

        # handle instalment order return
        elif returned_order.is_installment:
            order = order['data']
            draft = False
            partner_cash_paid = self.get_order_cash_paid(returned_order)
            order.update({
                'amount_paid': -partner_cash_paid,
                'amount_total': -partner_cash_paid,
                'amount_tax': -partner_cash_paid,
                'amount_return': partner_cash_paid,
            })
            returned_order.account_move.button_cancel()
            pos_session = self.env['pos.session'].browse(order['pos_session_id'])
            if pos_session.state == 'closing_control' or pos_session.state == 'closed':
                order['pos_session_id'] = self._get_valid_session(order).id

            pos_order = False
            if not existing_order:
                pos_order = self.create(self._order_fields(order))
            else:
                pos_order = existing_order
                pos_order.lines.unlink()
                order['user_id'] = pos_order.user_id.id
                pos_order.write(self._order_fields(order))

            pos_order = pos_order.with_company(pos_order.company_id)
            self = self.with_company(pos_order.company_id)
            self._process_payment_lines(order, pos_order, pos_session, draft)

            if not draft:
                try:
                    pos_order.action_pos_order_paid()
                except psycopg2.DatabaseError:
                    # do not hide transactional errors, the order(s) won't be saved!
                    raise
                except Exception as e:
                    _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
                pos_order._create_order_picking()

            if pos_order.to_invoice and pos_order.state == 'paid':
                pos_order._generate_pos_order_invoice()
            pos_order.write({'state': 'paid'})
            return pos_order.id
        else:
            return super(PosOrderInherit, self)._process_order(order, draft, existing_order)

    def is_fully_installment_paid(self, order_id):
        returned_order = self.env['pos.order'].browse(int(order_id))
        return any(line.installment_state != 'not_paid' for line in returned_order.account_move.installment_line_ids)


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _accumulate_amounts(self, data):
        """
        Override this function to filter orders to be reconciled when close session
        """
        amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
        tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
        split_receivables = defaultdict(amounts)
        split_receivables_cash = defaultdict(amounts)
        combine_receivables = defaultdict(amounts)
        combine_receivables_cash = defaultdict(amounts)
        invoice_receivables = defaultdict(amounts)
        sales = defaultdict(amounts)
        taxes = defaultdict(tax_amounts)
        stock_expense = defaultdict(amounts)
        stock_return = defaultdict(amounts)
        stock_output = defaultdict(amounts)
        rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
        # Track the receivable lines of the invoiced orders' account moves for reconciliation
        # These receivable lines are reconciled to the corresponding invoice receivable lines
        # of this session's move_id.
        order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
        rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
        # Filter orders
        order_ids = self.order_ids.filtered(lambda o: not (o.is_installment or o.return_order_ref.is_installment))
        for order in order_ids:
            # Combine pos receivable lines
            # Separate cash payments for cash reconciliation later.
            for payment in order.payment_ids:
                amount, date = payment.amountinstallment_line_ids, payment.payment_date
                if payment.payment_method_id.split_transactions:
                    if payment.payment_method_id.is_cash_count:
                        split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment],
                                                                               {'amount': amount}, date)
                    else:
                        split_receivables[payment] = self._update_amounts(split_receivables[payment],
                                                                          {'amount': amount}, date)
                else:
                    key = payment.payment_method_id
                    if payment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key],
                                                                             {'amount': amount}, date)
                    else:
                        combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount},
                                                                        date)

            if order.is_invoiced:
                # Combine invoice receivable lines
                key = order.partner_id
                if self.config_id.cash_rounding:
                    invoice_receivables[key] = self._update_amounts(invoice_receivables[key],
                                                                    {'amount': order.amount_paid}, order.date_order)
                else:
                    invoice_receivables[key] = self._update_amounts(invoice_receivables[key],
                                                                    {'amount': order.amount_total}, order.date_order)
                # side loop to gather receivable lines by account for reconciliation
                for move_line in order.account_move.line_ids.filtered(
                        lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
                    order_account_move_receivable_lines[move_line.account_id.id] |= move_line
            else:
                order_taxes = defaultdict(tax_amounts)
                for order_line in order.lines:
                    line = self._prepare_line(order_line)
                    # Combine sales/refund lines
                    sale_key = (
                        # account
                        line['income_account_id'],
                        # sign
                        -1 if line['amount'] < 0 else 1,
                        # for taxes
                        tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
                        line['base_tags'],
                    )
                    sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']},
                                                           line['date_order'])
                    # Combine tax lines
                    for tax in line['taxes']:
                        tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
                        order_taxes[tax_key] = self._update_amounts(
                            order_taxes[tax_key],
                            {'amount': tax['amount'], 'base_amount': tax['base']},
                            tax['date_order'],
                            round=not rounded_globally
                        )
                for tax_key, amounts in order_taxes.items():
                    if rounded_globally:
                        amounts = self._round_amounts(amounts)
                    for amount_key, amount in amounts.items():
                        taxes[tax_key][amount_key] += amount

                if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
                    # Combine stock lines
                    stock_moves = self.env['stock.move'].sudo().search([
                        ('picking_id', 'in', order.picking_ids.ids),
                        ('company_id.anglo_saxon_accounting', '=', True),
                        ('product_id.categ_id.property_valuation', '=', 'real_time')
                    ])
                    for move in stock_moves:
                        exp_key = move.product_id._get_product_accounts()['expense']
                        out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                        amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
                        stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount},
                                                                      move.picking_id.date, force_company_currency=True)
                        if move.location_id.usage == 'customer':
                            stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount},
                                                                         move.picking_id.date,
                                                                         force_company_currency=True)
                        else:
                            stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount},
                                                                         move.picking_id.date,
                                                                         force_company_currency=True)

                if self.config_id.cash_rounding:
                    diff = order.amount_paid - order.amount_total
                    rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)

                # Increasing current partner's customer_rank
                partners = (order.partner_id | order.partner_id.commercial_partner_id)
                partners._increase_rank('customer_rank')

        if self.company_id.anglo_saxon_accounting:
            global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
            if global_session_pickings:
                stock_moves = self.env['stock.move'].sudo().search([
                    ('picking_id', 'in', global_session_pickings.ids),
                    ('company_id.anglo_saxon_accounting', '=', True),
                    ('product_id.categ_id.property_valuation', '=', 'real_time'),
                ])
                for move in stock_moves:
                    exp_key = move.product_id._get_product_accounts()['expense']
                    out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                    amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
                    stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount},
                                                                  move.picking_id.date)
                    if move.location_id.usage == 'customer':
                        stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount},
                                                                     move.picking_id.date)
                    else:
                        stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount},
                                                                     move.picking_id.date)
        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

        data.update({
            'taxes': taxes,
            'sales': sales,
            'stock_expense': stock_expense,
            'split_receivables': split_receivables,
            'combine_receivables': combine_receivables,
            'split_receivables_cash': split_receivables_cash,
            'combine_receivables_cash': combine_receivables_cash,
            'invoice_receivables': invoice_receivables,
            'stock_return': stock_return,
            'stock_output': stock_output,
            'order_account_move_receivable_lines': order_account_move_receivable_lines,
            'rounding_difference': rounding_difference,
            'MoveLine': MoveLine
        })
        return data

    def _check_invoices_are_posted(self):
        # filter here with lines with only posted and not installment invoices
        # because we have canceled invoices came from returned orders

        unposted_invoices = self.order_ids.account_move.filtered(lambda x: x.state != 'posted' and not x.installment_paying)
        if unposted_invoices:
            raise UserError(_('You cannot close the POS when invoices are not posted.\n'
                              'Invoices: %s') % str.join('\n',
                                                         ['%s - %s' % (invoice.name, invoice.state) for invoice in
                                                          unposted_invoices]))

    def _reconcile_account_move_lines(self, data):
        # reconcile cash receivable lines
        split_cash_statement_lines = data.get('split_cash_statement_lines')
        combine_cash_statement_lines = data.get('combine_cash_statement_lines')
        split_cash_receivable_lines = data.get('split_cash_receivable_lines')
        combine_cash_receivable_lines = data.get('combine_cash_receivable_lines')
        order_account_move_receivable_lines = data.get('order_account_move_receivable_lines')
        invoice_receivable_lines = data.get('invoice_receivable_lines')
        stock_output_lines = data.get('stock_output_lines')

        for statement in self.statement_ids:
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_post()
            all_lines = (
                  split_cash_statement_lines[statement].mapped('move_id.line_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
                | combine_cash_statement_lines[statement].mapped('move_id.line_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
                | split_cash_receivable_lines[statement]
                | combine_cash_receivable_lines[statement]
            )
            accounts = all_lines.mapped('account_id')
            lines_by_account = [all_lines.filtered(lambda l: l.account_id == account and not l.reconciled) for account in accounts]
            for lines in lines_by_account:
                lines.reconcile()
            # We try to validate the statement after the reconciliation is done
            # because validating the statement requires each statement line to be
            # reconciled.
            # Furthermore, if the validation failed, which is caused by unreconciled
            # cash difference statement line, we just ignore that. Leaving the statement
            # not yet validated. Manual reconciliation and validation should be made
            # by the user in the accounting app.
            try:
                statement.button_validate()
            except UserError:
                pass

        # reconcile invoice receivable lines
        # filter here with lines with only posted invoice because we have canceled invoices came from returned orders
        for key in order_account_move_receivable_lines:
            ( order_account_move_receivable_lines[key]
            | invoice_receivable_lines.get(key, self.env['account.move.line'])
            ).filtered(lambda l: l.move_id.state == 'posted').reconcile()

        # reconcile stock output lines
        pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
        pickings |= self.order_ids.filtered(lambda o: not o.is_invoiced).mapped('picking_ids')
        stock_moves = self.env['stock.move'].search([('picking_id', 'in', pickings.ids)])
        stock_account_move_lines = self.env['account.move'].search([('stock_move_id', 'in', stock_moves.ids)]).mapped('line_ids')
        for account_id in stock_output_lines:
            ( stock_output_lines[account_id]
            | stock_account_move_lines.filtered(lambda aml: aml.account_id == account_id)
            ).filtered(lambda aml: not aml.reconciled).reconcile()
        return data
