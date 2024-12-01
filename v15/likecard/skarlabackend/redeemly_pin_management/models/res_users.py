import base64
import functools
import logging
import re
import secrets
import string
import uuid
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.addons.auth_totp.models.totp import TOTP
from odoo.exceptions import UserError
from odoo.tools.config import config

_logger = logging.getLogger(__name__)

compress = functools.partial(re.sub, r'\s', '')


class SubMerchantPermission(models.Model):
    _name = 'sub.merchant.permission'

    name_arabic = fields.Char(string="Name In Arabic")
    name_english = fields.Char(string="name In English")
    code = fields.Char(string="Code")
    category = fields.Selection(
        [('products', 'Products'), ("reports", 'Reports'), ('orders', 'Orders'), ('codes', 'Codes'),
         ('invoices', 'Invoices'), ('wallet', 'Wallet')],
        string='Status', readonly=True, copy=False, index=True, tracking=3)

    def serialize_for_api(self, id=False):
        return {
            'id': self.id,
            'name_arabic': self.name_arabic,
            'name_english': self.name_english if self.name_english else "",
            'code': self.code,
            "enabled": True if self.id in self.env["res.users"].sudo().search(
                [("id", '=', id)]).permission_id.ids else False,
            'category': self.category,
        }


class UserInherited(models.Model):
    _inherit = 'res.users'

    is_merchant = fields.Boolean(string='Merchant')
    is_sub_merchant = fields.Boolean(string='Sub Merchant', default=False)
    parent_merchant = fields.Many2one('res.users', string="Parent Merchant",
                                      domain=[('is_merchant', '=', True), ('is_sub_merchant', '=', False)], index=True)
    permission_id = fields.Many2many('sub.merchant.permission', string="Permissions For Sub Merchant")
    is_service_provider = fields.Boolean(string='Service Provider')
    is_accountant = fields.Boolean(string='Is Accountant')
    is_accountant_manager = fields.Boolean(string='Is Accountant Manager')
    accountant_manager_sps_ids = fields.Many2many('res.users', 'res_users_res_user_rel', 'acc_manager_id', 'sp_id',
                                                  string="Accountant Manager's Assigned Service Providers",
                                                  domain=[('is_service_provider', '=', True)],
                                                  default=lambda self: self._default_accountant_manager_sps_ids()
                                                  )

    reference = fields.Char(string='Reference', copy=False, readonly=True,
                            index=True, default=lambda self: _('New'))
    redeemly_api_key = fields.Char(string="REDEEMLY API KEY", unique=True)
    fees_value = fields.Float(string='Pull Fees Value', digits=(16, 6))
    redeem_fees_value = fields.Float(string='Redeem Fees Value', digits=(16, 6))
    # ------ tech fields ------
    invites_ids = fields.One2many('merchant.package.invites', inverse_name='merchant')
    first_login = fields.Boolean(string='First Login', default=True)
    key_creation_time = fields.Datetime(string='token creation time')
    token_random = fields.Char(string='token')
    enable_low_stock_notification = fields.Boolean(string='Enable Low Stock Notification')
    stock_limit = fields.Integer(string='Stock Limit')
    enable_low_balance_notification = fields.Boolean(string='Enable Low Balance Notification')
    balance_limit = fields.Integer(string='Balance Limit')
    notification_to_email = fields.Char(string='Stock Notification To Email')
    balance_notification_to_email = fields.Char(string='balance Notification To Email')
    sp_hash = fields.Char(string="SP Hash")
    blocked_user = fields.Boolean(string='Blocked User', default=False)
    portal_welcome_text = fields.Text(string='Portal Welcome Text')
    # white_labeling = fields.Char(unique=True)
    last_six_digit_for_2f = fields.Char()
    last_six_digit_for_2f_reation_time = fields.Datetime(string='token creation time')

    last_session_id_2_factor = fields.Char()
    last_session_id_2_factor_time = fields.Datetime(string='token creation time')
    enable_invoice_auto_generating = fields.Boolean(string='Enable Invoice Auto Generating', default=False)
    invoice_generating_frequency = fields.Selection(selection=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='daily')
    merchant_invoice_mail = fields.Char('Merchant Invoice Mail')
    sp_currency = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    codes_additional_value = fields.Selection(selection=[
        ('secret', 'secret'),
        ('email_with_redeem', 'Email With Redeem'),
        ('net_dragon', 'net dragon'),
    ], default=None)
    netdragon_account_name = fields.Char(string="Netdragon Account Name")
    netdragon_account_secret = fields.Char(string="Netdragon Account Secret")

    foodics_random_state = fields.Char()
    foodics_bearar_token = fields.Char(string="FOODICS API KEY", unique=True)
    is_foodics_cashier = fields.Boolean(string='Is Foodics Cashier')

    # SP finance
    is_sp_finance = fields.Boolean(string='IS SP Finance')
    finance_service_provider_id = fields.Many2one('res.users', string='Service Provider',
                                                  domain=[('is_service_provider', '=', True)])
    # Categories
    default_categ_id = fields.Many2one('product.category')
    archived_products_categ_id = fields.Many2one('product.category')
    categs_ids = fields.Many2many('product.category')

    # sp vendors
    vendor_ids = fields.One2many('res.partner', 'vendor_user_id', string='Vendors', domain=[('is_vendor', '=', True)])

    # sp redeem websites
    website_key_ids = fields.One2many('website.api.key', 'user_id', string='Websites API keys')

    @api.constrains('fees_value')
    def check_fees_value(self):
        for rec in self:
            if rec.fees_value > 1 or rec.fees_value < 0:
                raise UserError("Fees is percentage between 0 and 1")

    @api.onchange('is_accountant_manager')
    def _onchange_is_accountant_manager(self):
        if not self.is_accountant_manager:
            self.accountant_manager_sps_ids = self._default_accountant_manager_sps_ids()

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = str(uuid.uuid4()).replace("-", '')

        vals['redeemly_api_key'] =UserInherited.generate_api_key()
        vals['sp_hash'] = uuid.uuid4()
        res = super(UserInherited, self).create(vals)
        if vals.get('is_service_provider'):
            main_category, archived_category = res.create_main_and_archived_category()
        return res

    def write(self, vals):
        result = super(UserInherited, self).write(vals)

        if vals.get('is_service_provider'):
            self.create_main_and_archived_category()

        if vals.get('is_accountant_manager'):
            self.accountant_manager_sps_ids = self._default_accountant_manager_sps_ids()

        return result

    @api.model
    def _default_accountant_manager_sps_ids(self):
        return self.env['res.users'].search([('is_service_provider', '=', True)])

    def regenerate_api_key(self):
        self.sudo().redeemly_api_key = UserInherited.generate_api_key()
        return self.redeemly_api_key

    @staticmethod
    def generate_api_key():
        """Generate a random API key using a UUID."""
        api_key = str(uuid.uuid4()).replace("-", '').upper()
        api_key += str(uuid.uuid4()).replace("-", '').upper()
        return api_key

    def get_user_roles(self):
        roles = []
        if self.is_merchant:
            if self.is_sub_merchant:
                roles.append('submerchant')
            else:
                roles.append('merchant')
        if self.is_service_provider:
            roles.append('service_provider')
        if self.is_accountant_manager:
            roles.append('accountant Manager')
        if self.is_sp_finance:
            roles.append('sp_finance')
        return roles

    def get_permissions(self):
        permissions = [
            item.serialize_for_api(self.id) for item in self.permission_id
        ]

        return permissions

    def change_password_and_send_email(self, front_url):
        token = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(10))
        self.key_creation_time = datetime.now()
        self.token_random = token
        template = self.env.ref('redeemly_pin_management.skarla_reset_password')
        context = {'server_base_url': config.get('server_base_url'), 'token': token,
                   "front_url": config.get('front_url') + front_url}
        template.with_context(context).send_mail(self.id)

    def serialize_for_api(self, id=False):
        return {
            'id': self.id,
            'name': self.name,
            'login': self.login if self.login else "",
            'is_merchant': self.is_merchant,
            'reference': self.reference,
            "all_merchant_invitations": [
                item.serialize_for_api(item.id) for item in self.invites_ids
            ]
            # 'white_labeling': self.white_labeling if self.white_labeling else "",
        }

    def serialize_for_api_sps(self, user):
        sps = user.accountant_manager_sps_ids
        return [
            {"id": sp.id, "name": sp.name} for sp in sps
        ]

    # Start 2 factor authentication
    def _mfa_url_api(self):
        r = super()._mfa_url()
        if r is not None:
            return r
        if self._mfa_type() == 'totp_mail':
            return '/web/login/totp'

    def _totp_check_api(self, code):
        sudo = self.sudo()
        key = base64.b32decode(sudo.totp_secret)
        match = TOTP(key).match(code)
        if match is None:
            return False
        return True

    def _totp_try_setting_api(self, secret, code):
        if self.totp_enabled or self != self.env.user:
            return False
        secret = compress(secret).upper()
        match = TOTP(base64.b32decode(secret)).match(code)
        if match is None:
            return False
        self.sudo().totp_secret = secret
        # if request:
        #     self.flush()
        #     # update session token so the user does not get logged out (cache cleared by change)
        #     new_token = self.env.user._compute_session_token(request.session.sid)
        #     request.session.session_token = new_token
        return True

    def _totp_try_setting_api_refresh(self, secret, code):
        if self.totp_enabled and self == self.env.user:
            secret = compress(secret).upper()
            match = TOTP(base64.b32decode(secret)).match(code)
            if match is None:
                return False
        self.sudo().totp_secret = secret
        # if request:
        #     self.flush()
        #     # update session token so the user does not get logged out (cache cleared by change)
        #     new_token = self.env.user._compute_session_token(request.session.sid)
        #     request.session.session_token = new_token
        return True

    def action_totp_disable_api(self):
        logins = ', '.join(map(repr, self.mapped('login')))
        if not (self == self.env.user or self.env.user._is_admin() or self.env.su):
            # _logger.info("2FA disable: REJECT for %s (%s) by uid #%s", self, logins, self.env.user.id)
            return False

        self.revoke_all_devices()
        self.sudo().write({'totp_secret': False})

        # if request and self == self.env.user:
        #     self.flush()
        #     # update session token so the user does not get logged out (cache cleared by change)
        #     new_token = self.env.user._compute_session_token(request.session.sid)
        #     request.session.session_token = new_token
        return True
        # _loggerinfo("2FA disable: SUCCESS for %s (%s) by uid #%s", self, logins, self.env.user.id)
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'type': 'warning',
        #         'message': _("Two-factor authentication disabled for the following user(s): %s", ', '.join(self.mapped('name'))),
        #         'next': {'type': 'ir.actions.act_window_close'},
        #     }
        # }

    def check_low_stock_notification(self):
        try:
            sps = self.env['res.users'].search(
                [('is_service_provider', '=', True), ('enable_low_stock_notification', '=', True)])
            for sp in sps:
                query = """
                    SELECT pt.service_provider_id, pt.id, pt.name, pt."SKU", count(*) FROM PUBLIC.PRODUCT_SERIALS ps
                        join PUBLIC.PRODUCT_TEMPLATE pt on pt.id = ps.product_id
                        join PUBLIC.batch_serials bs on bs.id = ps.batch_id
                        where pt.is_prepaid = False
                        and pt.service_provider_id = %s
                        and bs.state = '1'
                        and ps.state = '1'
                        group by service_provider_id, pt.id, pt.name,pt."SKU"
                        having count(*) <= %s
                """
                self._cr.execute(query, [sp.id, sp.stock_limit])
                res = self._cr.fetchall()
                template = self.env.ref('redeemly_pin_management.low_stock_email_tempalte')
                if res:
                    email_values = {
                        'email_from': 'noreply@skarla.com'
                    }
                    template.with_context(data=res).send_mail(sp.id, email_values=email_values)
        except Exception as e:
            _logger.info("skarla_cron check low stock notification")
            _logger.exception(e)
            self.env.cr.rollback()

    def check_low_balance_notification(self):
        try:
            merchants = self.env['res.users'].search(
                [('is_merchant', '=', True), ('enable_low_balance_notification', '=', True)])
            for merchant in merchants:
                limit = merchant.balance_limit
                query = """
                     SELECT 
                        partner.id,
                        partner.name,
                        partner.email,
                        partner.balance
                    FROM 
                        PUBLIC.res_partner partner
                    WHERE 
                        partner.balance <= %s
                         AND partner.id = %s;
                    """
                self._cr.execute(query, [limit, merchant.partner_id.id])
                res = self._cr.fetchall()
                template = self.env.ref('redeemly_pin_management.low_balance_email_tempalte')
                if res:
                    email_values = {
                        'email_from': 'noreply@skarla.com'
                    }
                    template.with_context(data=res).send_mail(merchant.id, email_values=email_values)
        except Exception as e:
            _logger.info("skarla_cron low balance notification")
            _logger.exception(e)
            self.env.cr.rollback()

    def generate_six_code_for_verify_refresh_2f(self):
        ### generate serial code random from 16 characters , each 4 characters seperated by - ###
        id = uuid.uuid4()
        random_string = str(id.int)[:6]

        # Split the string into 4-character parts
        parts = [random_string[i:i + 4] for i in range(0, len(random_string), 4)]

        # Join the parts with a "-"
        result = "".join(parts)
        view_result = "".join(parts)
        ###   where result variable represent serial_code ###
        print("#######################################")
        print(result)
        return result

    def send_email_verify_2_factor(self, refresh_route):
        self.last_six_digit_for_2f = self.generate_six_code_for_verify_refresh_2f()
        self.last_six_digit_for_2f_reation_time = datetime.now()
        template = self.env.ref('redeemly_pin_management.skarla_refresh_2f')
        context = {'server_base_url': config.get('server_base_url'),
                   'last_six_digit_for_2f': self.last_six_digit_for_2f,
                   "front_url": config.get('front_url') + refresh_route}
        template.with_context(context).send_mail(self.id)

    def set_last_session_id_2_factor(self):
        self.last_session_id_2_factor = uuid.uuid4()
        self.last_session_id_2_factor_time = datetime.now()

    # deactivate portal accounts to implement in test env
    def deactivate_test_accounts(self):

        date_one_month_ago = datetime.now() - relativedelta(months=1)
        portals = self.search([('groups_id', 'in', self.env.ref('base.group_portal').id),
                               ('create_date', '<=', date_one_month_ago)])
        if portals:
            portals.active = False

    @api.model
    def _get_login_domain(self, login):
        return [('login', '=ilike', login)]

    # def fill_users_with_categ_id(self):
    #
    #     sps_products = self.env['product.template'].sudo().search([('service_provider_id', 'in', self.ids)])
    #     archived_sps_products = self.env['product.template'].sudo().search(
    #         [('service_provider_id', 'in', self.ids), ('active', '=', False)])
    #     for rec in self:
    #         if rec:
    #             main_category_id, archived_category_id = rec.create_main_and_archived_category()
    #             rec_products = sps_products.filtered(lambda p: p.service_provider_id == rec)
    #             if rec_products:
    #                 all_products_categ = self.env['product.category'].sudo().create({
    #                     "service_provider_id": rec.id,
    #                     "name": "All Products",
    #                     "name_ar": "جميع المنتجات",
    #                     "parent_id": main_category_id,
    #                     "image_url":"https://redeemly-odoo.s3.me-south-1.amazonaws.com/redeemly-odoo/odoo/e3e4a4ad6c498543e8157ca20dee57297c441643"
    #                 })
    #                 rec_products.write({'categ_id': all_products_categ.id})
    #
    #             rec_archived_products = archived_sps_products.filtered(lambda p: p.service_provider_id == rec)
    #             if rec_archived_products:
    #                 archived_sps_products.write({'categ_id': archived_category_id})

    def create_main_and_archived_category(self):
        default_categ_id = self.env['product.category'].sudo().create({
            "service_provider_id": self.id,
            "name": "Main Category For SP #" + str(self.id),
        })
        self.default_categ_id = default_categ_id

        archived_products_categ_id = self.env['product.category'].sudo().create({
            "service_provider_id": self.id,
            "name": "Archived Products Category For SP #" + str(self.id)
        })
        self.archived_products_categ_id = archived_products_categ_id
        return self.default_categ_id.id, self.archived_products_categ_id.id

    def fill_old_accountant_managers_users_with_related_sps(self):
        users_without_related_sps = self.search([('is_accountant_manager', '=', True),
                                                 ('accountant_manager_sps_ids', '=', False)])
        users_without_related_sps.accountant_manager_sps_ids = self._default_accountant_manager_sps_ids()
