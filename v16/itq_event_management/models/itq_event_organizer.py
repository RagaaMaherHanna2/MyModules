from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItqEventOrganizer(models.Model):
    _name = 'itq.event.organizer'
    _inherit = ['mail.thread']
    _description = "Event Organizer"

    name = fields.Char(string="Name", required=True, tracking=True)
    manager = fields.Char(string="Manager", required=True, tracking=True)
    email = fields.Char(string="Email", required=True, tracking=True)
    phone = fields.Char(string="Phone", required=True, tracking=True)
    member_ids = fields.One2many(comodel_name='itq.organizer.member', inverse_name='event_organizer_id',
                                 string="Members")

    _sql_constraints = [('name', 'unique (name)', 'The name must be unique per event !')]

    @api.constrains('member_ids')
    def _check_member_count(self):
        for record in self:
            if not record.member_ids:
                raise ValidationError(_("The event must have at least one person in the event."))
