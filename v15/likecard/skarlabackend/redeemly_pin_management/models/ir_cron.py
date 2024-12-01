from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _name = 'ir.cron'
    _inherit = ['ir.cron', 'mail.thread']
