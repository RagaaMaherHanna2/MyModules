from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqEventManagementSettings(models.Model):
    _name = 'itq.event.management.settings'
    _inherit = ['mail.thread']
    _description = _("Event Management Settings")

    name = fields.Char(string="Main Settings", translate=True, tracking=True)
    event_instructions = fields.Html(string="Instructions", tracking=True, help="Events instructions in HTML format.")
