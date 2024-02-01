from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqEntranceConfiguration(models.Model):
    _name = "itq.entrance.configuration"
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Entrance Configuration')

    name = fields.Char(required=True, string="Entrance Name", tracking=True)
    branch_id = fields.Many2one('itq.holding.branch', required=True, ondelete='restrict', tracking=True,
                                domain="[('state', '=', 'active')]", default=lambda self: self.get_default_branch())
    map_location = fields.Char(tracking=True)

    @api.constrains('name', 'branch_id')
    def constraint_unique_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('branch_id', '=', rec.branch_id.id), ('id', '!=', rec.id)]):
                raise ValidationError(
                    _('The entrance {} already exist at {}').format(rec.name, rec.branch_id.name))

    @api.model
    def get_default_branch(self):
        return self.env['itq.holding.branch'].search(
            [('state', '=', 'active'), ('is_default_branch', '=', True)], limit=1)
