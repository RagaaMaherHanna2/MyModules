from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItqOrganizerTeam(models.Model):
    _name = 'itq.organizer.team'
    _inherit = 'itq.abstract.validate.field.format'
    _description = "Organizer Team"

    event_request_id = fields.Many2one('itq.event.request', required=True, ondelete='cascade', tracking=True)
    name = fields.Char(string="Name", required=True, tracking=True)
    title = fields.Char(string="Title", required=True, tracking=True)
    mobile = fields.Char(string="mobile", required=True, tracking=True)

    @api.constrains('mobile')
    def check_mobile(self):
        for record in self:
            if record.mobile and not self._validate_phone_number(record.mobile):
                raise ValidationError(_("Invalid mobile format"))
