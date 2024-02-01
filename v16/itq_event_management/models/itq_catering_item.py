from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItqCateringItem(models.Model):
    _name = 'itq.catering.item'
    _inherit = ['mail.thread']
    _description = _("Catering Item")

    name = fields.Char(string="Catering Item", required=True, tracking=True)
    # quantity = fields.Integer(string='Quantity')
    catering_type_id = fields.Many2one(comodel_name="itq.catering.type", string="Catering Type", ondelete='restrict')

    @api.constrains('name', 'catering_type_id')
    def constraint_unique_name_and_catering_type_id(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name),
                                  ('catering_type_id', '=', rec.catering_type_id.id),
                                  ('id', '!=', rec.id)]):
                raise ValidationError(_('You cannot duplicate catering item.'))
