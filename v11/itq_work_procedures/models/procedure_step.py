# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProcedureStep(models.Model):
    _name = 'procedure.step'
    _description = "Procedure Step"

    _sql_constraints = [
        ("unique_name", "UNIQUE (name,procedure_id)",
         _("Steps names must be unique for the same procedure."))
    ]
    sequence = fields.Char(string="Sequence", compute='_sequence_ref')
    name = fields.Char(string='Step Name', required=True)
    procedure_id = fields.Many2one('work.procedure')
    description = fields.Char(string='Description', required=True)
    system = fields.Char(string='System')
    communication_tool = fields.Char(string='Communication Tool')
    execution_days = fields.Integer(string='Execution Days')
    execution_hours = fields.Integer(string='Execution Hours')
    execution_mints = fields.Integer(string='Execution Mints')

    @api.depends('procedure_id.procedure_step_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.procedure_id.procedure_step_ids:
                no += 1
                l.sequence = no

    def action_view_step_resources(self):
        self.ensure_one()
        tree_id = self.env.ref('itq_work_procedures.procedure_resource_view_tree').id
        form_id = self.env.ref('itq_work_procedures.procedure_resource_view_form').id
        return {
            'name': _('Procedure Resource'),
            'type': 'ir.actions.act_window',
            'res_model': 'procedure.resource',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('step_id', '=', self.id)],
            'target': 'new',
        }

    def action_view_step_docs(self):
        self.ensure_one()
        tree_id = self.env.ref('itq_work_procedures.procedure_document_view_tree').id
        form_id = self.env.ref('itq_work_procedures.procedure_document_view_form').id
        return {
            'name': _('Procedure Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'procedure.document',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('step_id', '=', self.id)],
            'target': 'new',
        }
