from odoo import models, fields, api


class ItqAbstractEventGuest(models.AbstractModel):
    _name = 'itq.abstract.event.guest'

    name = fields.Char(required=True, tracking=True, string="Guest Name")
    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade')
    has_event_permission = fields.Boolean(string="Has Event Permission", compute="compute_has_event_permission",
                                          store=True)
    event_state = fields.Selection(related='event_request_id.state', readonly=True)

    @api.depends('event_request_id', 'event_request_id.event_permission_ids',
                 'event_request_id.event_permission_ids.state',
                 'event_request_id.event_permission_ids.permission_invitee_ids')
    def compute_has_event_permission(self):
        for record in self:
            if record.event_request_id.event_permission_ids.filtered(lambda p: p.state != 'canceled').mapped(
                    'permission_invitee_ids').filtered(lambda e: e.res_id == record.id and e.res_model == record._name):
                record.has_event_permission = True
            else:
                record.has_event_permission = False
