from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    related_collect_custody_ids = fields.Many2many('itq.collect.custody.request',
                                                   string='Related Collect Custody Requests')
