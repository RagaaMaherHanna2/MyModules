import uuid
import datetime
from odoo import models, fields, api, _
from hashlib import sha256

from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.exceptions import UserError



class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'


   number_email_sended = fields.Integer(string="Number Of Email Sened For Redeem Product Card", help="# Email Sended In Job Or Cron For Redeem Product Card" , config_parameter='redeemly_pin_management.number_email_sended')
   control_panel_url_redeem_history = fields.Char(string = "Control Panel URL For redeem History " , config_parameter='redeemly_pin_management.control_panel_url_redeem_history' )
   number_invoice_request_sp = fields.Integer(string = "Number Of invoices Request Processed By Service Provider" , config_parameter='redeemly_pin_management.number_invoice_request_sp')
   number_invoice_request_sys = fields.Integer(string = "Number Of invoices Request Processed By System" , config_parameter='redeemly_pin_management.number_invoice_request_sys')

   @api.depends('company_id')
   def _compute_has_chart_of_accounts(self):
      self.has_chart_of_accounts = bool(self.company_id.chart_template_id)
      self.has_accounting_entries = True
