# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_create_requisition(self):
        form_view_id = self.env.ref("itq_purchases_requisition.itq_purchase_requisition_form").id
        task_project = self.env['itq.purchase.project'].search([('itq_main_lookup_res_id', '=', self.project_id.id)])
        print(task_project.name)
        print(self.name)
        print(self.id)
        return {
            'name': _('Purchase Requisition'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'itq.purchase.requisition',
            'views': [(form_view_id, 'form')],
            'target': 'current',
            'context': {'default_task_id': self.id, 'default_project_id': task_project.id,
                        'default_project_is_readonly': True},
        }
