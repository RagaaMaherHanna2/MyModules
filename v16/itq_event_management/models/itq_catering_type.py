from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItqCateringType(models.Model):
    _name = 'itq.catering.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _("Catering Type")

    name = fields.Char(string="Type", translate=True, tracking=True)
    is_mandatory = fields.Boolean(string="Mandatory", required=True, tracking=True)
    catering_item_ids = fields.One2many(comodel_name='itq.catering.item', inverse_name='catering_type_id',
                                        string="Catering Items")

    @api.constrains('catering_item_ids')
    def _constraint_catering_item_ids_count(self):
        for record in self:
            if not record.catering_item_ids:
                raise ValidationError(_("You must have at least one catering item."))
