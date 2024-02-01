# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ProcedureScope(models.Model):
    _name = 'procedure.scope'
    _description = "Procedure Scope"

    _sql_constraints = [
        ("unique_name", "UNIQUE (name)", _("This Scope Name has been registered before."))
    ]

    name = fields.Char(string="Scope Name", required=True, track_visibility='onchange')
    description = fields.Text(string="Description")
    active_scope = fields.Boolean(default=True)
