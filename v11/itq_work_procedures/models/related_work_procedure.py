# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RelatedWorkProcedure(models.Model):
    _name = 'related.work.procedure'
    _description = "Related Work Procedure"

    _sql_constraints = [
        ("unique_related_procedure_procedure_id", "UNIQUE (related_procedure_id,procedure_id)",
         _("This Procedure is already attached with parent procedure before."))
    ]
    serial_number = fields.Integer(string='Serial Number', compute='_sequence_ref')
    procedure_id = fields.Many2one('work.procedure')
    related_procedure_id = fields.Many2one('work.procedure', required=True, domain=lambda x: x.get_procedure_domain())
    user_id = fields.Many2one('res.users', string='Another User', default=lambda self: self.env.user.id, readonly=True,
                              required=True)
    related_procedure_version = fields.Char(related='related_procedure_id.version_no')
    relation = fields.Char(string='Relation Description', required=True)

    @api.depends('procedure_id.related_procedure_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.procedure_id.related_procedure_ids:
                no += 1
                l.serial_number = no

    @api.model
    def get_procedure_domain(self):
        available_procedures_ids = self.env['work.procedure'].search(
            [('id', '!=', self.procedure_id.id), ('state', '=', 'confirmed'),
             ('department_id', '=', self.procedure_id.department_id.id)
             ]).ids
        return [('id', 'in', available_procedures_ids)]
