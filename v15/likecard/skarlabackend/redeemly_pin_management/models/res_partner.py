from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.config import config


class PartnerInherited(models.Model):
    _inherit = 'res.partner'

    integration = fields.Char(string="Integration Class",
                              help="Determine the class which implements API integration with the service provider")

    balance = fields.Float(string="Balance")
    balance_in_other_currency = fields.Char(string="Balance In Other Currency",
                                            compute='compute_balance_in_other_currency')
    partner_logo_url = fields.Char(string='Partner Logo URL', compute="compute_partner_logo_url")

    vendor_user_id = fields.Many2one('res.users', ondelete='cascade')
    is_vendor = fields.Boolean(string="Is Vendor?")

    @api.onchange("partner_logo_url")
    def compute_partner_logo_url(self):
        for rec in self:
            attachment = self.env['ir.attachment'].search(
                [("res_model", "=", "res.partner"), ('res_id', '=', rec.id),
                 ('res_field', '=', 'image_1920')])
            if attachment:
                rec.partner_logo_url = attachment[0].url
            else:
                rec.partner_logo_url = ""

    def _increase_rank(self, field, n=1):
        pass

    # def compute_balance(self):
    #     for rec in self:
    #         rec.balance = rec.get_balance()

    def compute_balance_in_other_currency(self):
        for rec in self:
            if self.property_purchase_currency_id:
                rec.balance_in_other_currency = str(-1 * rec.get_balance_in_other_currency()) + " " + str(
                    self.property_purchase_currency_id.name)
            else:
                rec.balance_in_other_currency = "N/A"

    def get_balance(self):
        self = self.sudo()
        self.ensure_one()
        debit_account_id = self.env.ref('redeemly_pin_management.account_wallet_debit')
        domain = [('partner_id', '=', self.id), ('move_id.state', '=', 'posted'), ('account_id', '=', debit_account_id.id)]
        sql = """
            select sum(balance) from public.account_move_line aml 
                where account_id = %s
                and parent_state = 'posted'
                and partner_id=%s
        """
        self._cr.execute(sql, [debit_account_id.id, self.id])
        balance = self._cr.fetchall()
        # lines = self.env['account.move.line'].search(domain)
        # balance = 0
        # for line in lines:
        #     balance += line.balance
        return balance[0][0] if balance[0][0] else 0

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email or "",
            'logo': self.partner_logo_url or "",
            'portal_welcome_text': self.user_ids.portal_welcome_text or ""
        }

    def compute_balance_after_change(self):
        sql = """
        update public.res_partner pp set balance = (
            select sum(balance) from public.account_move_line aml 
                            where account_id = 44
                            and parent_state = 'posted'
                            and partner_id= pp.id
            )
            where id in (select partner_id from public.res_users where is_merchant = True )
        """
        self._cr.execute(sql)