# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ItqPurchaseRequisition(models.Model):
    _inherit = 'itq.purchase.requisition'

    task_id = fields.Many2one('project.task', string="Task")
    is_out_of_task_lines = fields.Boolean(compute='_compute_lines_status')
    is_qty_exceeded_lines = fields.Boolean(compute='_compute_lines_status')
    project_is_readonly = fields.Boolean(default=False)

    @api.onchange('project_id')
    def onchange_account_ids(self):
        self.ensure_one()
        domain = []
        if self.project_id:
            if not self.project_is_readonly:
                self.task_id = False
            tasks = self.env['project.project'].search([('id', '=', self.project_id.itq_main_lookup_res_id)]).mapped(
                'tasks')
            if tasks:
                domain = [('id', 'in', tasks.ids)]
        return {'domain': {'task_id': domain}}

    @api.depends('task_id', 'purchase_requisition_line_ids')
    def _compute_lines_status(self):
        """
        this compute function computes the requisition lines state if some of it's demanded items is out of planned
        items in mentioned task,
         or it exceeds the planned qty of this item in the task.
        """
        for rec in self:
            is_out_of_task_lines = is_qty_exceeded_lines = False
            if rec.task_id and rec.purchase_requisition_line_ids:
                task_material_lines = rec.task_id.material_plan_ids
                task_consumed_lines = rec.task_id.consumed_material_ids
                out_of_task_lines = rec.purchase_requisition_line_ids.filtered(
                    (lambda l: l.product_id not in task_material_lines.mapped('product_id')))
                in_task_lines = rec.purchase_requisition_line_ids.filtered(
                    (lambda l: l.product_id in task_material_lines.mapped('product_id')))
                if out_of_task_lines:
                    is_out_of_task_lines = True
                    out_of_task_lines.line_state = 'out_of_task'
                if in_task_lines:
                    line_state = 'validated'
                    requisition_lines = [{'product_id': product,
                                          'qty': sum(in_task_lines.filtered(lambda l: l.product_id == product).mapped(
                                              'uom_demand_quantity')),
                                          'ids': in_task_lines.filtered(lambda l: l.product_id == product).mapped('id')}
                                         for product in in_task_lines.mapped('product_id')]
                    for line in requisition_lines:
                        product_another_qty = 0.0
                        product_material_qty = sum(
                            task_material_lines.filtered(lambda l: l.product_id == line['product_id']).mapped(
                                'product_uom_qty'))
                        product_consumed_qty = sum(
                            task_consumed_lines.filtered(lambda l: l.product_id == line['product_id']).mapped(
                                'product_uom_qty'))
                        product_another_lines = self.env['itq.purchase.requisition.line'].search([
                            ('product_id', '=', line['product_id'].id),
                            ('purchase_requisition_id', '!=', rec.id),
                            ('purchase_requisition_id.state', '!=', 'cancelled'),
                            ('purchase_requisition_id.task_id', '=', rec.task_id.id),
                        ])
                        if product_another_lines:
                            product_another_qty = sum(product_another_lines.mapped('uom_demand_quantity'))
                        if (line['qty'] + product_another_qty) > (product_material_qty - product_consumed_qty):
                            line_state = 'qty_exceeded'
                            is_qty_exceeded_lines = True
                        rec.purchase_requisition_line_ids.filtered(
                            lambda l: l.id in line['ids']).line_state = line_state

            rec.is_out_of_task_lines = is_out_of_task_lines
            rec.is_qty_exceeded_lines = is_qty_exceeded_lines


class ItqPurchaseRequisitionLine(models.Model):
    _inherit = 'itq.purchase.requisition.line'

    line_state = fields.Selection([('validated', 'Validated'),
                                   ('qty_exceeded', 'Qty Exceeded'),
                                   ('out_of_task', 'Out Of Planned')], default='validated')
    uom_demand_quantity = fields.Float(string="Demand Quantity", compute='_compute_uom_demand_quantity')

    @api.depends('demand_quantity', 'product_uom')
    def _compute_uom_demand_quantity(self):
        uom_demand_quantity = 0.0
        for rec in self:
            if rec.demand_quantity or rec.product_uom:
                uom_demand_quantity = rec.product_uom._compute_quantity(rec.demand_quantity, rec.product_id.uom_id)
            rec.uom_demand_quantity = uom_demand_quantity
