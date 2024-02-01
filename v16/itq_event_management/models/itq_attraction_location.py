from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqAttractionLocation(models.Model):
    _name = 'itq.attraction.location'
    _inherit = ['itq.abstract.event.lookup']
    _description = _('Location Attraction')

    name = fields.Char(string="Location Attraction", required=True, tracking=True)
    seating_type_ids = fields.Many2many('itq.event.seating.type', string="Allowed Seating Types"
                                        , domain="[('state', '=', 'active')]", tracking=True)
    minimum_guest_count = fields.Integer(string="Min Number Of Guests ", default=1, tracking=True)
    maximum_guest_count = fields.Integer(string="Max Number Of Guests", default=1, tracking=True)
    branch_id = fields.Many2one('itq.holding.branch', string='Branch', ondelete='restrict',
                                domain="[('state', '=', 'active')]", tracking=True)
    event_request_ids = fields.One2many('itq.event.request', 'event_attraction_id', string="Event Request",
                                        ondelete='cascade', tracking=True)
    resource_calendar_id = fields.Many2one(comodel_name='resource.calendar', string="Working Schedule",
                                           ondelete='restrict', tracking=True)
    is_event = fields.Boolean(string="Is Event", default=True, tracking=True)
    is_visit = fields.Boolean(string="Is Visit", default=True, tracking=True)
    is_photo_shoot = fields.Boolean(string="Is Photo Shoot", default=True, tracking=True)

    @api.constrains('minimum_guest_count', 'maximum_guest_count')
    def _check_positive_values(self):
        for record in self:
            if record.minimum_guest_count < 1:
                raise ValidationError(_("Minimum Guest Count cannot be less than 1"))
            if record.maximum_guest_count < record.minimum_guest_count:
                raise ValidationError(_("Minimum Guest Count cannot be greater than Maximum Guest Count"))

    def activate_button(self):
        seats = self.seating_type_ids.filtered(lambda seat: seat.state != 'active')
        if seats:
            raise ValidationError(_('Seating Types must be active!'))
        super(ItqAttractionLocation, self).activate_button()

    def show_events(self):
        self.ensure_one()
        return {
            'name': _('Attraction Events'),
            'view_mode': 'calendar,tree,form',
            'res_model': 'itq.event.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('event_attraction_id', '=', self.id), ('state', '!=', 'rejected')]
        }

    def unlink(self):
        for rec in self:
            if rec == self.env.ref('itq_event_management.other_attraction_location'):
                raise ValidationError(_("You can not delete this record."))
        return super(ItqAttractionLocation, self).unlink()
