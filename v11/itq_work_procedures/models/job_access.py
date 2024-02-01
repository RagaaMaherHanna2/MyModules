# -*- coding: utf-8 -*-

from odoo import models, fields, _


class JobAccess(models.Model):
    _name = 'job.access'
    _description = "Job Access"

    _sql_constraints = [
        ("unique_job_access_name", "UNIQUE (name)", _("This Job Access Name has been registered before."))
    ]

    name = fields.Char(string='Access Name', required=True)
    description = fields.Text(string="Description")
    procedure_id = fields.Many2one('work.procedure')
    active_job = fields.Boolean(default=True)
