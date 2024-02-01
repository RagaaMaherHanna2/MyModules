from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AmenitiesItems(models.Model):
    _name = "itq.amenity.item"
    _description = _('Amenities Items')

    name = fields.Char(required=True)
    amenity_specification_id = fields.Many2one('itq.amenity.specification', ondelete='restrict')

    @api.constrains('name')
    def check_unique_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]):
                raise ValidationError(_('You cannot duplicate {}.').format(_(rec.name)))
