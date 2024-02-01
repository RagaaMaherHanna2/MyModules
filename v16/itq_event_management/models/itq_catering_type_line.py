from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ItqCateringTypeLine(models.Model):
    _name = "itq.catering.type.line"
    _inherit = 'mail.thread'
    _description = _("Catering Type Line")

    catering_type_id = fields.Many2one('itq.catering.type', ondelete='restrict', required=True, string="Catering",
                                       tracking=True, domain=[('state', '=', 'active')])
    catering_item_ids = fields.Many2many('itq.catering.item', string="Items",
                                         domain="[('catering_type_id', '=', catering_type_id)]", tracking=True,
                                         required=True)
    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade', tracking=True)

    @api.constrains('catering_type_id')
    def check_catering_type_id(self):
        for record in self:
            if self.search_count(
                    [('catering_type_id', '=', record.catering_type_id.id),
                     ('event_request_id', '=', record.event_request_id.id), ('id', '!=', record.id)]):
                raise ValidationError(_('You cannot duplicate {}.').format(_(record.catering_type_id.name)))

    @api.onchange('catering_type_id')
    def _onchange_catering_type_id(self):
        self.catering_item_ids = False

    @api.constrains('catering_item_ids')
    def check_catering_item_ids(self):
        for record in self:
            if not record.catering_item_ids:
                raise ValidationError(_('Items must have at least one item'))
