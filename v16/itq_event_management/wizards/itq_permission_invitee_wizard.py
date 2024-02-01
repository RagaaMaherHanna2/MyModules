from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqPermissionInviteeWizard(models.TransientModel):
    _name = "itq.permission.invitee.wizard"

    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade', required=1, readonly=1)
    permission_id = fields.Many2one('itq.event.permission', string='Permission', ondelete='cascade')
    permission_state = fields.Selection(related='permission_id.state', readonly=True)
    guest_list_ids = fields.Many2many('itq.invitee', string='Guest List',
                                      domain="[('event_request_id', '=', event_request_id),"
                                             "('has_event_permission', '=', False)]")
    guest_honors_ids = fields.Many2many('itq.guest.honor', string='Guest Honors',
                                        domain="[('event_request_id', '=', event_request_id),"
                                               "('has_event_permission', '=', False)]")
    guest_speaker_ids = fields.Many2many('itq.speaker.guest', string='Guest Speakers',
                                         domain="[('event_request_id', '=', event_request_id),"
                                                "('has_event_permission', '=', False)]")

    def save(self):
        self.ensure_one()
        self.create_permission_invitee(self.guest_list_ids)
        self.create_permission_invitee(self.guest_honors_ids)
        self.create_permission_invitee(self.guest_speaker_ids)

    def add_invitee_to_permission(self):
        self.ensure_one()
        record = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
        self.create_permission_invitee(record)

    def create_permission_invitee(self, guest_ids):
        self.ensure_one()
        permission_invitee_obj = self.env['itq.permission.invitee']
        for guest in guest_ids:
            if permission_invitee_obj.search_count(
                    [('res_id', '=', guest.id), ('res_model', '=', guest._name),
                     ('permission_id', '=', self.permission_id.id)]) and self.permission_state != 'canceled':
                raise ValidationError(_("You have selected this person before."))
            else:
                permission_invitee_obj.create({
                    'res_model': guest._name,
                    'res_id': guest.id,
                    'permission_id': self.permission_id.id})
