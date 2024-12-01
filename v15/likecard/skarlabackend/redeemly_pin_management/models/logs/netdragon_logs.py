from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class NetDragonLog(models.Model):
    _name = 'netdragon.log'

    validate_request_id = fields.Char(string="Validate Request ID")
    username = fields.Char(string="username")
    code = fields.Char(string="code")
    validate_request_body = fields.Char("Valdiate Request body JSON")
    validate_response_result = fields.Char(string="Validate Response Result JSON")
    topup_request_body = fields.Char("Topup Request body JSON")
    topup_response_body = fields.Char("Topup Response Result JSON")
    our_message = fields.Char("Our Result")
