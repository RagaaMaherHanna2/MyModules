# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    requisition_ids = fields.Many2many('itq.purchase.requisition', 'Project Requisitions',
                                       compute='_compute_requisitions_count')
    requisitions_count = fields.Integer('Requisitions Count', compute='_compute_requisitions_count')

    def _compute_requisitions_count(self):
        for rec in self:
            rec.requisition_ids = self.env['itq.purchase.requisition'].search(
                [('project_id.itq_main_lookup_res_id', '=', self.id)])
            rec.requisitions_count = len(rec.requisition_ids)

    def get_project_requisitions(self):
        # task_requisitions = self.env['itq.purchase.requisition'].search(
        #     [('project_id.itq_main_lookup_res_id', '=', self.id)])
        tree_view_id = self.env.ref("itq_purchases_requisition.itq_purchase_requisition_tree").id
        form_view_id = self.env.ref("itq_purchases_requisition_project.itq_purchase_requisition_view_form2").id
        task_project = self.env['itq.purchase.project'].search([('itq_main_lookup_res_id', '=', self.id)])
        return {
            'name': _('Purchase Requisition'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'itq.purchase.requisition',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'target': 'current',
            'context': {'default_project_id': task_project.id, },
            'domain': [('id', 'in', self.requisition_ids.ids)]
        }
