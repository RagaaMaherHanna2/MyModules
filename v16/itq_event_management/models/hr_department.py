from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    resource_calendar_id = fields.Many2one(comodel_name='resource.calendar', string="Working Schedule",
                                           ondelete='restrict', tracking=True)
    is_visitable = fields.Boolean(string="Is Visitable", default=True, tracking=True)
    is_research_department = fields.Boolean(string="Is Research Department", tracking=True)

    @api.onchange('is_visitable')
    def _onchange_is_visitable(self):
        self.is_research_department = False
