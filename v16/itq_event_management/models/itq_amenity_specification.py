from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AmenitiesAndSpecifications(models.Model):
    _name = "itq.amenity.specification"
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Amenities And Specifications')

    name = fields.Char(string="Preparation", tracking=True)
    is_mandatory = fields.Boolean(string="Mandatory", tracking=True)
    amenity_item_ids = fields.One2many('itq.amenity.item', 'amenity_specification_id',
                                       string="Items", tracking=True)

    @api.constrains('amenity_item_ids')
    def check_amenities_items_ids(self):
        for record in self:
            if not record.amenity_item_ids:
                raise ValidationError(_('Amenities Items should not be empty .'))
