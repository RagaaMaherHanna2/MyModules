from odoo import api, fields, models, _


class ItqOrganizerMember(models.Model):
    _name = 'itq.organizer.member'
    _inherit = ['mail.thread']
    _description = "Organizer Member"

    event_organizer_id = fields.Many2one(comodel_name='itq.event.organizer', string="Organization", ondelete='cascade')
    name = fields.Char(string="Name", required=True, tracking=True)
    phone = fields.Char(string="Phone", required=True, tracking=True)
