import uuid
import datetime
from odoo import models, fields, api, _
from hashlib import sha256
import logging
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools import config
_logger = logging.getLogger(__name__)


class product_serial_redeem_history(models.Model):
    _name = 'redeem.history.prepaid'

    product_serial = fields.Many2one('product.serials', index=True)
    date = fields.Datetime(string = "Redeem Date")
    value = fields.Integer(string = 'Value Redeemed')
    user_id = fields.Char(string = "User Id")
    transaction_id = fields.Char(string = "Transaction ID")
    email_sent = fields.Boolean(string = "Email Sent" , default=True )
    product_attributes_value = fields.One2many('product.attribute.values', inverse_name='history_id')
    website_api_key_id = fields.Many2one('website.api.key', 'Website API Key')
    def serialize_for_api(self):
        self.ensure_one()
        product = self.product_serial.product_id
        return {
            'id': self.id,
            'date': datetime.datetime.strftime(self.date, DATETIME_FORMAT),
            'value': self.value,
            'user_id': self.user_id,
            'transaction_id': self.transaction_id,
            'product': {
                'id': product.id,
                'name': product.name,
                'serial_number': self.product_serial.serial_number,
                'is_prepaid': product.is_prepaid,
                "use_skarla_portal": product.use_skarla_portal
            },
            "product_attributes_value": [item.serialize_for_api() for item in self.product_attributes_value],
            'website_api_key': self.website_api_key_id.website_redeemly_api_key if self.website_api_key_id else "",
            'website_name': self.website_api_key_id.name if self.website_api_key_id else "",
        }

    def process_send_email(self):
        # try:
        not_sent_yet = self.search([('email_sent', '=', True)] , order='id' ,limit=100)
        email_values = {
            'email_from': 'noreply@skarla.com'
        }
        for redeem_operation in not_sent_yet:
            context = {'server_base_url': config.get('server_base_url') }
            if redeem_operation.product_serial.product_id.is_prepaid:
                template = self.env.ref('redeemly_pin_management.redeem_history_email_tempalte')
                template.with_context(context).send_mail(redeem_operation.id, email_values=email_values)
            if redeem_operation.product_serial.product_id.service_provider_id.codes_additional_value == 'email_with_redeem':
                template = self.env.ref('redeemly_pin_management.redeem_history_for_with_email_users')
                context['redeem_detail_operation'] = config.get('front_url') + "/en-GB/dashboard/redeem-history/details/" + str(redeem_operation.id)
                template.with_context(context).send_mail(redeem_operation.id, email_values=email_values)
            if redeem_operation.product_serial.product_id.service_provider_id.codes_additional_value == 'net_dragon':
                template = self.env.ref('redeemly_pin_management.redeem_history_for_net_dragon_client')
                template.with_context(context).send_mail(redeem_operation.id, email_values=email_values)
            redeem_operation.email_sent = False
        # except Exception as e:
        #     _logger.info("skarla_cron Process Send Email")
        #     _logger.exception(e)
        #     self.env.cr.rollback()

    def create(self, vals_list):
        res = super(product_serial_redeem_history, self).create(vals_list)
        for rec in res:
            fees = rec.product_serial.product_id.service_provider_id.redeem_fees_value
            if fees > 0:
                journal_id = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
                debit_account_id = self.env.ref('redeemly_pin_management.account_wallet_debit')
                date = fields.date.today()
                lines = []
                lines.append({
                    'account_id': debit_account_id.id,
                    'credit': fees,
                    'debit': 0,
                    'fees_type': '1',
                    'name': "Credit Your Wallet, fees percentage: %s" % (str(fees)),
                    'currency_id': rec.product_serial.product_id.service_provider_id.sp_currency.id,
                    'partner_id': rec.product_serial.product_id.service_provider_id.partner_id.id,
                })
                lines.append({
                    'account_id': debit_account_id.id,
                    'credit': 0,
                    'debit': fees,
                    'name': "Debit Company Wallet, fees percentage: %s" % (str(fees)),
                    'currency_id': rec.product_serial.product_id.service_provider_id.sp_currency.id,
                    'partner_id': 1,
                })
                journal = self.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'date': date,
                    'package_product_id': rec.product_serial.product_id.id,
                    'line_ids': [(0, 0, line) for line in lines],
                    'journal_id': journal_id.id
                })
                journal.action_post()

