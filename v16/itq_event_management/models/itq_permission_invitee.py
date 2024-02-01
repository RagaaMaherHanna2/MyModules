from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

INVITEE_FIELDS = ['name', 'email', 'phone', 'title']
class ItqPermissionInvitee(models.Model):
    _name = 'itq.permission.invitee'
    _inherit = 'itq.abstract.validate.field.format'
    _description = 'Permission Invitee'

    name = fields.Char(string='Name', required=True, readonly=True, compute='_compute_resource_fields')
    title = fields.Char(string='Title', readonly=True, compute='_compute_resource_fields')
    email = fields.Char(string='Email', readonly=True, compute='_compute_resource_fields')
    phone = fields.Char(string='Phone', readonly=True, compute='_compute_resource_fields')
    res_id = fields.Integer(readonly=True)
    res_model = fields.Char(readonly=True)
    permission_id = fields.Many2one('itq.event.permission', ondelete='cascade', required=True)

    @api.constrains('email')
    def check_email_unique(self):
        for record in self:
            if record.email and self.search_count(
                    [('email', '=', record.email), ('permission_id', '=', record.permission_id.id),
                     ('id', '!=', record.id)]) > 0:
                raise ValidationError(_("we have a person with same email"))

    @api.constrains('phone')
    def check_mobile(self):
        for record in self:
            if record.phone and not record._validate_phone_number(record.phone):
                raise ValidationError(_("Invalid invitee's phone format"))

    @api.constrains('email')
    def check_email(self):
        for record in self:
            if record.email and not record._validate_email(record.email):
                raise ValidationError(_("Invalid invitee's email format"))

    @api.model
    def _get_resource_record(self, res_id, res_model):
        return self.env[res_model].browse(res_id)

    @api.depends('res_id', 'res_model')
    def _compute_resource_fields(self):
        for record in self:
            resource = self._get_resource_record(record.res_id, record.res_model)
            if resource:
                for field in INVITEE_FIELDS:
                    if field in resource._fields:
                        record[field] = getattr(resource, field)
                    else:
                        record[field] = ""
