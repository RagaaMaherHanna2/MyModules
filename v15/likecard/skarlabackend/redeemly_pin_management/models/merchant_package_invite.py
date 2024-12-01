import datetime
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.addons.redeemly_pin_management.controllers.wallet_controller import RedeemlyWalletManagement

from odoo import models, fields, api, _
from odoo.tools import config


class MerchantPackageInvite(models.Model):
    _name = 'merchant.package.invites'
    _inherit = ['mail.thread']

    _description = 'Merchant Package Invites'

    merchant = fields.Many2one(
        comodel_name='res.users', domain=[('is_merchant', '=', True)])
    product = fields.Many2one(
        comodel_name='product.template', ondelete='cascade')
    price = fields.Float('Price', required=True)
    limit = fields.Integer("Pull Limit")
    unlimited = fields.Boolean(string='unlimited')
    # pulled_codes_count = fields.Integer("Pulled Codes", compute="_compute_pulled_codes_count")
    pulled_serials_count = fields.Integer("Pulled Codes", compute="_compute_pulled_serials_count")

    expiry_date = fields.Datetime('Expiration Date', default=False)
    enabled = fields.Boolean("Enabled", default=True)
    email_sent = fields.Boolean(string='Email Invitation Sent', default=False)
    tax_id = fields.Many2one('account.tax', string='Tax Id')
    _sql_constraints = [
        ('invite_unique', 'unique(merchant,product)', 'This merchant is already invited.')
    ]

    def _compute_pulled_serials_count(self):
        self = self.sudo()
        for rec in self:
            rec.pulled_serials_count = self.env['product.serials'].search_count(
                [('product_id', 'in', rec.product.ids), ('pulled_by', '=', rec.merchant.id)])

    def get_all_merchant_product(self):
        merchant_invites = self.search([('merchant', '=', self.merchant.id),
                                        ('product.service_provider_id', '=', self.product.service_provider_id.id)])
        return [
            item.serialize_for_api() for item in merchant_invites.product
        ]

    def deduct_balance(self, total_amount, product_quantity_group_by):
        self.ensure_one()
        # get fees according to service provider
        fees = self.product.service_provider_id.fees_value
        journal_id = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
        debit_account_id = self.env.ref('redeemly_pin_management.account_wallet_debit')
        date = fields.date.today()
        for product, quantity in product_quantity_group_by.items():
            lines = []
            fees_amount = quantity['quantity'] * fees
            # credit merchant wallet
            amount_credit = quantity['quantity'] * self.price

            if self.tax_id:
                if self.tax_id.amount_type == 'percent':
                    amount_credit = amount_credit + (amount_credit * self.tax_id.amount / 100)
                else:
                    amount_credit = amount_credit + self.tax_id.amount

            lines.append({
                'account_id': debit_account_id.id,
                'credit': amount_credit,
                'debit': 0,
                'name': "Credit Your Wallet, Pull Operation %s , Product: %s, Quantity: %s" %(self.merchant.reference, str(quantity['name']), str(quantity['quantity'])),
                'currency_id': self.product.service_provider_id.sp_currency.id,
                'partner_id': self.merchant.partner_id.id,
            })
            # debit
            lines.append({
                'account_id': debit_account_id.id,
                'credit': 0,
                'debit': quantity['quantity'] * self.price,
                'name': "Debit Your Wallet. Pull Operation From Merchant: %s, Product: %s, Quantity: %s" % (self.merchant.reference, str(quantity['name']), str(quantity['quantity'])),
                'currency_id': self.product.service_provider_id.sp_currency.id,
                'partner_id': self.product.service_provider_id.partner_id.id,
            })
            # if there tax id
            if self.tax_id:
                lines.append({
                    'account_id': self.tax_id.invoice_repartition_line_ids.mapped('account_id').id,
                    'credit': 0,
                    'debit': amount_credit - quantity['quantity'] * self.price,
                    'name': "Wallet deducted from merchant For Tax",
                    'currency_id': self.product.service_provider_id.sp_currency.id,
                    'partner_id': self.product.service_provider_id.partner_id.id,
                })

            # if fees_amount > 0:
            #     lines.append({
            #         'account_id': debit_account_id.id,
            #         'credit': fees_amount,
            #         'debit': 0,
            #         'fees_type': '2',
            #         'name': "Credit Your Wallet, fees percentage: %s" % (str(fees)),
            #         'currency_id': self.product.service_provider_id.sp_currency.id,
            #         'partner_id': self.product.service_provider_id.partner_id.id,
            #     })
            #     lines.append({
            #         'account_id': debit_account_id.id,
            #         'credit': 0,
            #         'debit': fees_amount,
            #         'name': "Debit Company Wallet, fees percentage: %s" % (str(fees)),
            #         'currency_id': self.product.service_provider_id.sp_currency.id,
            #         'partner_id': 1,
            #     })
            journal = self.env['account.move'].sudo().create({
                'name': str(datetime.datetime.now()) + "-Pull Operation-" + self.merchant.reference,
                'move_type': 'entry',
                'date': date,
                'package_product_id': product,
                'invite_id': self.id,
                'line_ids': [(0, 0, line) for line in lines],
                'journal_id': journal_id.id
            })
            journal.action_post()

    def serialize_for_api(self, id=False, with_all_products=False):
        return {
            "id": self.id,
            "merchant": {
                "id": self.merchant.id,
                "name": self.merchant.name,
                "reference": self.merchant.reference
            },
            "image": self.product.get_product_image_url(),
            "product": self.product.name,
            "product_id": self.product.id,
            "is_prepaid": self.product.is_prepaid,
            "price": self.price,
            'unlimited': self.unlimited,
            "limit": self.limit if not self.unlimited else -1,
            'pulled_serials_count': self.pulled_serials_count,
            "remaining_qty": self.limit - self.pulled_serials_count if not self.unlimited else -1,
            "enabled": self.enabled,
            "balance": RedeemlyWalletManagement.get_user_balance(self.merchant),
            "product_details": self.product.serialize_for_api() if id else {},
            "tax_id": self.tax_id.serialize_for_api() if self.tax_id else {},
            "codes_additional_value": self.product.service_provider_id.codes_additional_value
            # "all_product_merchants": self.get_all_merchant_product() if with_all_products else {}
        }

    def _send_email_invitation(self):
        not_sent_yet = self.search([('email_sent', '=', False)])
        template = self.env.ref('redeemly_pin_management.package_invitaiton_email_tempalte')
        email_values = {
            'email_from': 'noreply@skarla.com'
        }

        for invite in not_sent_yet:
            context = {'server_base_url': config.get('server_base_url') }
            template.with_context(context).send_mail(invite.id, email_values=email_values)
            invite.email_sent = True
