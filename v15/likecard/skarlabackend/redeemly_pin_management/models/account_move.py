from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.config import config
import calendar

class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    invite_id = fields.Many2one('merchant.package.invites')
    package_product_id = fields.Many2one('product.template')

    def serialize_for_api(self):
        self.ensure_one()
        bank_request = self.env['pin.management.bank.transfer.request'].search([('invoice_id', '=', self.id)])
        return {
            'id': self.id,
            'invoice_date': datetime.strftime(self.invoice_date, DATETIME_FORMAT),
            'state': self.payment_state,
            'payment_request_id': [b.id for b in bank_request],
            'bank_transfer_state': [b.state for b in bank_request],
            'total': self.amount_total,
            'lines': [{
                'name': line.name,
                'price_unit': line.price_unit
            } for line in self.invoice_line_ids]
        }


class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    fees_type = fields.Selection(selection=[
        ('1', 'redeem'),
        ('2', 'pull'),
        ('3', 'invoiced'),
    ], default=None, index=True)

    def generate_fees_invoices(self, process_all_sp=True):
        try:
            users = self.env['res.users'].search([('is_service_provider', '=', True)])
            limit = int(config.get('number_invoice_request_sp'))
            processed_count = 0
            for user in users:
                if processed_count >= limit:
                    break

                last_invoice = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                                ('partner_id', '=', user.partner_id.id),
                                                                ('state', 'in', ['draft', 'posted']),
                                                                ], order="id desc", limit=1)
                last_invoice_date = last_invoice.date
                to_invoice_date = datetime.now().replace(day=1) - timedelta(days=1)

                if last_invoice_date and last_invoice_date.month >= datetime.now().date().month:
                    continue
                if last_invoice_date and last_invoice_date.month < datetime.now().date().month:
                    from_invoice_date = last_invoice_date + timedelta(days=1)
                    sql = """
                               select SUM(sol.product_uom_qty), product.id, product.name from public.sale_order so
                               join public.sale_order_line sol on so.id = sol.order_id
                               join public.product_template product on product.id = sol.product_id
                               where  
                               so.date_order >= %s
                               and so.date_order <= %s
                               and so.service_provider_id = %s
                               group by product.id, product.name
                       """
                    self._cr.execute(sql, [
                        datetime(from_invoice_date.year, from_invoice_date.month, from_invoice_date.day, 0, 0, 0),
                        datetime(to_invoice_date.year, to_invoice_date.month, to_invoice_date.day, 0, 0, 0),
                        user.id
                    ])
                else:
                    sql = """
                           select SUM(sol.product_uom_qty), product.id, product.name from public.sale_order so
                           join public.sale_order_line sol on so.id = sol.order_id
                           join public.product_template product on product.id = sol.product_id
                           where  
                           so.date_order <= %s
                           and so.service_provider_id = %s
                           group by product.id, product.name
                       """
                    self._cr.execute(sql, [
                        datetime(to_invoice_date.year, to_invoice_date.month, to_invoice_date.day, 23, 59, 59),
                        user.id
                        ]
                                     )
                data = self._cr.fetchall()
                if data and data[0][0]:
                    if user.fees_value > 0:
                        invoice = self.env['account.move'].create({
                            'move_type': 'out_invoice',
                            'partner_id': user.partner_id.id,
                            'invoice_date': to_invoice_date,
                            'invoice_line_ids': [
                                {
                                    'name': data[0][2],
                                    'account_id': self.env.ref('redeemly_pin_management.fees_revenue_account').id,
                                    'quantity': data[0][0],
                                    'price_unit': user.fees_value
                                }
                            ]
                        })
                        invoice.action_post()
                        processed_count = processed_count + 1
        except Exception as e:
            _logger.info("skarla_cron Process fees invoices")
            _logger.exception(e)
            self.env.cr.rollback()