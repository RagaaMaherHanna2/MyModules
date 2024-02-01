from odoo import fields, models, _


class ItqEventSeatingType(models.Model):
    _name = 'itq.event.seating.type'
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Event Seating Type')

    name = fields.Char(string="Seating Type", required=True, tracking=True)
