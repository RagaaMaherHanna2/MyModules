from odoo import models, fields, _


class ItqTargetAudience(models.Model):
    _name = "itq.target.audience"
    _inherit = 'itq.abstract.event.lookup'
    _description = _('Target Audience')
