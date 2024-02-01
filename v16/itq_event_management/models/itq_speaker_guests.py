from odoo import fields, models, _, api


class ItqSpeakerGuest(models.Model):
    _name = 'itq.speaker.guest'
    _inherit = ['mail.thread', 'itq.abstract.event.guest']
    _description = _("Speaker Guests")

    title = fields.Char(required=True, tracking=True, string="Guest Title")
    organization = fields.Char(string="Organization", required=True, tracking=True)
    is_insider = fields.Boolean(string="Insider", default=False, tracking=True)

