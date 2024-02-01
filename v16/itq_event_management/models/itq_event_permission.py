import base64
from io import BytesIO
import qrcode
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqEventPermission(models.Model):
    _name = 'itq.event.permission'
    _description = 'Event Permission'

    name = fields.Char(string='Source', tracking=True, related='event_request_id.request_number', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')],
                             default='draft', tracking=True, required=1, readonly=1)
    permission_number = fields.Char(string='Permission Number', readonly=True, tracking=True)
    branch_id = fields.Many2one('itq.holding.branch', string='Branch', ondelete='restrict',
                                related="event_request_id.event_attraction_id.branch_id", readonly=True)
    entrance_ids = fields.Many2many('itq.entrance.configuration', string='Entrance', tracking=True)
    number_of_guests = fields.Integer(string="Number Of Guests", tracking=True, required=True)
    permission_start_date = fields.Datetime(string="Permission Start Date", readonly=True,
                                            related="event_request_id.event_date")
    permission_end_date = fields.Datetime(string="Permission End Date", readonly=True,
                                          related="event_request_id.event_date_end")
    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade', required=True,
                                       domain="[('state', '=', 'confirmed')]", tracking=True, string='Event')
    qr_code = fields.Binary("QR Code", compute='generate_qr_code')

    # Permission Invitee
    permission_invitee_ids = fields.One2many('itq.permission.invitee', 'permission_id', tracking=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'event.permission.sequence')], limit=1)
        vals['permission_number'] = sequence.next_by_id()
        return super(ItqEventPermission, self).create(vals)

    @api.constrains('event_request_id')
    def _check_event_request_id(self):
        for record in self:
            if record.event_request_id.state != 'confirmed':
                raise ValidationError(_('Event request must be confirmed.'))

    def set_confirmed(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'confirmed'})
        else:
            raise ValidationError(_('State cannot be changed to confirmed.'))

    def set_canceled(self):
        self.ensure_one()
        if self.state in ['draft', 'confirmed']:
            self.write({'state': 'canceled'})
        else:
            raise ValidationError(_('State cannot be changed to canceled.'))

    def generate_qr_code(self):
        if qrcode and base64:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5,
                               border=5, )
            menu_id = self.env.ref('itq_event_management.itq_event_permission_menu').id

        for rec in self:
            url = f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web#id={rec.id}&cids=1&model={self._name}&view_type=form&menu_id={menu_id}"
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            rec.update({'qr_code': qr_image})

    @api.constrains('number_of_guests')
    def _check_number_of_guests(self):
        for record in self:
            if record.number_of_guests < 0:
                raise ValidationError(_('Number of guests must be greater than 0.'))

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}  + {}".format(_("Event "), str(record.name) or '')))
        return result

    @api.onchange('event_request_id')
    def count_number_of_guests(self):
        self.number_of_guests = self.event_request_id.expected_number_of_guests