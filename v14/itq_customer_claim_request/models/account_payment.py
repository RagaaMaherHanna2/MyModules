from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self.env.context.get('from_claim_request'):
            if self._context.get('skip_account_move_synchronization'):
                return

            for pay in self.with_context(skip_account_move_synchronization=True):

                # After the migration to 14.0, the journal entry could be shared between the account.payment and the
                # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
                if pay.move_id.statement_line_id:
                    continue

                move = pay.move_id
                move_vals_to_write = {}
                payment_vals_to_write = {}

                if 'journal_id' in changed_fields:
                    if pay.journal_id.type not in ('bank', 'cash'):
                        raise UserError(_("A payment must always belongs to a bank or cash journal."))

                if 'line_ids' in changed_fields:
                    all_lines = move.line_ids
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                    if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal entry must always contains:\n"
                            "- one journal item involving the outstanding payment/receipts account.\n"
                            "- one journal item involving a receivable/payable account.\n"
                            "- optional journal items, all sharing the same account.\n\n"
                        ) % move.display_name)

                    # if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    #     raise UserError(_(
                    #         "The journal entry %s reached an invalid state relative to its payment.\n"
                    #         "To be consistent, all the write-off journal items must share the same account."
                    #     ) % move.display_name)
                    #
                    if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal items must share the same currency."
                        ) % move.display_name)

                    if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal items must share the same partner."
                        ) % move.display_name)

                    if not pay.is_internal_transfer:
                        if counterpart_lines.account_id.user_type_id.type == 'receivable':
                            payment_vals_to_write['partner_type'] = 'customer'
                        else:
                            payment_vals_to_write['partner_type'] = 'supplier'

                    liquidity_amount = liquidity_lines.amount_currency

                    move_vals_to_write.update({
                        'currency_id': liquidity_lines.currency_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })
                    payment_vals_to_write.update({
                        'amount': abs(liquidity_amount),
                        'currency_id': liquidity_lines.currency_id.id,
                        'destination_account_id': counterpart_lines.account_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })
                    if liquidity_amount > 0.0:
                        payment_vals_to_write.update({'payment_type': 'inbound'})
                    elif liquidity_amount < 0.0:
                        payment_vals_to_write.update({'payment_type': 'outbound'})

                move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
                pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))
        else:
            return super(AccountPayment, self)._synchronize_from_moves(changed_fields)