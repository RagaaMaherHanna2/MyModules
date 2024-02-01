from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ItqAmenitySpecificationLine(models.Model):
    _name = "itq.amenity.specification.line"
    _inherit = 'mail.thread'
    _description = _('Amenities And Specifications Line')

    amenity_specification_id = fields.Many2one('itq.amenity.specification', ondelete='restrict', required=True,
                                               string="Amenity", tracking=True, domain=[('state', '=', 'active')])
    amenity_item_ids = fields.Many2many('itq.amenity.item', string="Items", tracking=True, required=True,
                                        domain="[('amenity_specification_id', '=', amenity_specification_id)]")
    event_request_id = fields.Many2one('itq.event.request', ondelete='cascade', tracking=True)

    @api.constrains('amenity_specification_id')
    def check_amenity_specification_id(self):
        for record in self:
            if self.search_count(
                    [('amenity_specification_id', '=', record.amenity_specification_id.id),
                     ('event_request_id', '=', record.event_request_id.id), ('id', '!=', record.id)]):
                raise ValidationError(_('You cannot duplicate {}.').format(_(record.amenity_specification_id.name)))

    @api.onchange('amenity_specification_id')
    def _onchange_amenity_specification_id(self):
        self.amenity_item_ids = False

    @api.constrains('amenity_item_ids')
    def check_amenity_item_ids(self):
        for record in self:
            if not record.amenity_item_ids:
                raise ValidationError(_('Items must have at least one item'))
