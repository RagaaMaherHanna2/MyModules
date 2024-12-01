# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
import datetime

class MailNotification(models.Model):
    _inherit = 'mail.notification'

    notification_type = fields.Selection(selection_add=[
        ('back', 'Back-Office')
    ], ondelete={'back': 'cascade'})
    # sms_id = fields.Many2one('sms.sms', string='SMS', index=True, ondelete='set null')
    # sms_number = fields.Char('SMS Number')
    # failure_type = fields.Selection(selection_add=[
    #     ('sms_number_missing', 'Missing Number'),
    #     ('sms_number_format', 'Wrong Number Format'),
    #     ('sms_credit', 'Insufficient Credit'),
    #     ('sms_server', 'Server Error'),
    #     ('sms_acc', 'Unregistered Account')
    # ])
    #bank_tranfer_id = fields.Many2one("pin.management.bank.transfer.request")

    # we use display name to text message of notification
    #invoice_request_id = fields.Many2one("merchant.invoice.request")


class Mail_message(models.Model):
    _inherit = 'mail.message'

    is_read = fields.Boolean()
    skarla_dashboard = fields.Boolean(default=False)

    def serialize_for_api(self):
        return {
            'id':self.id,
            'date': datetime.datetime.strftime(self.date, DATETIME_FORMAT),
            "subject": self.subject,
            "body": self.body,
            "model":self.model,
            "res_id": self.res_id,
            "is_read": self.is_read,
        }
