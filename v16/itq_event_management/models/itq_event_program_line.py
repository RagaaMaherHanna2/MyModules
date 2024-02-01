from odoo import api, models, fields, api, _
from odoo.exceptions import ValidationError


class ItqEventProgramLine(models.Model):
    _name = "itq.event.program.line"
    _inherit = 'mail.thread'
    _description = _('Event Program Line')

    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade', tracking=True)
    day_line_id = fields.Many2one('itq.day.line', required=1,
                                  domain="[('name', '<=', parent.event_number_of_days)]",
                                  ondelete='restrict', tracking=True, string="Day")
    time = fields.Float(required=True, tracking=True)
    activity = fields.Text(required=True, tracking=True)

    @api.constrains('day_line_id', 'time')
    def constraint_of_day_and_time(self):
        for rec in self:
            if self.search_count([('day_line_id', '=', rec.day_line_id.id),
                                  ('time', '=', rec.time),
                                  ('event_request_id', '=', rec.event_request_id.id),
                                  ('id', '!=', rec.id)]):
                raise ValidationError(_('You cannot create two event program with the same date.'))

    @api.constrains('time')
    def constraint_time(self):
        for rec in self:
            if rec.time >= 24 or rec.time < 0:
                raise ValidationError(_('Time must be greater than or equal 00:00 and less than 24:00'))
