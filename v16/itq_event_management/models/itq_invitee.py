from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqInvitee(models.Model):
    _name = 'itq.invitee'
    _inherit = ['itq.abstract.validate.field.format', 'itq.abstract.event.guest']
    _description = 'Itq Invitee'

    name = fields.Char(string='Invitee name', required=True, tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    nationality = fields.Char(string='Nationality', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    identification = fields.Char(string='Identification', tracking=True)

    @api.constrains('mobile')
    def check_mobile(self):
        for record in self:
            if record.mobile and not self._validate_phone_number(record.mobile):
                raise ValidationError(_("Invalid invitee's mobile format"))

    @api.constrains('email')
    def check_email(self):
        for record in self:
            if record.email and not self._validate_email(record.email):
                raise ValidationError(_("Invalid invitee's email format"))

    @api.constrains('identification')
    def check_identification(self):
        for record in self:
            if record.identification and self.search_count(
                    [('identification', '=', record.identification), ('id', '!=', record.id),
                     ('event_request_id', '=', record.event_request_id.id)]) > 0:
                raise ValidationError(_("we have a person with same identification"))

    @api.constrains('name')
    def check_name(self):
        for record in self:
            if not record.name.strip():
                raise ValidationError(_("invitee name is required"))
