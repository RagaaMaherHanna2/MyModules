from odoo import fields, models, _, api


class ItqGuestHonor(models.Model):
    _name = 'itq.guest.honor'
    _inherit = ['mail.thread', 'itq.abstract.event.guest']
    _description = _("Guests Of Honor")

    title = fields.Char(required=True, tracking=True, string="Guest Title")
    organization = fields.Char(string="Organization", required=True, tracking=True)
    is_insider = fields.Boolean(string="Insider", default=False, tracking=True)
