# -*- coding: utf-8 -*-
from odoo import models, fields,api, _


class ProcedureName(models.Model):
    _name = 'procedure.name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Procedure Name"

    _sql_constraints = [
        ("unique_name", "UNIQUE (name)", _("This Name has been registered before."))
    ]

    code = fields.Char(readonly=True)
    name = fields.Char(string="Name", required=True, track_visibility='onchange')
    description = fields.Text(string="Description")
    name_active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('procedure.name.seq')
        vals['code'] = code

        return super(ProcedureName, self).create(vals)