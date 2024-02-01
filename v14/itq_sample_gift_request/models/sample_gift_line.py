# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SampleGiftLine(models.Model):
    _name = 'sample.gift.line'
    _description = 'Sample Gift Line'
    _rec_name = 'product_id'

    sample_id = fields.Many2one('sample.gift.request', string='Sample')
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, )
    branch_id = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id, )
    user_id = fields.Many2one('res.users', related='sample_id.user_id')
    branch_manager_id = fields.Many2one('res.users', related='sample_id.branch_manager_id')

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float('Quantity')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom = fields.Many2one('uom.uom', string='Product UOM', required=True,
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_serial_lines = fields.One2many('product.serial.line', 'sample_line_id', string='Product Serials')

    lot_ids = fields.Many2many('stock.production.lot', string='Lots/Serials', compute='_compute_lot_ids')

    @api.model
    def create(self, vals):
        line_code = self.env['ir.sequence'].next_by_code('sample.gift.request.line.seq')
        if 'branch_id' in vals:
            branch = self.env['res.branch'].browse(vals['branch_id'])
            line_code = branch.code + line_code
        vals['name'] = line_code
        return super(SampleGiftLine, self).create(vals)

    @api.constrains('product_qty', 'product_serial_lines')
    def _constrains_product_qty(self):
        for rec in self:
            product_ava_qty = sum(self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),
                                                                  ('location_id', '=',
                                                                   rec.sample_id.warehouse_location_id.id)]).mapped(
                'available_quantity'))
            if rec.product_qty > product_ava_qty:
                raise ValidationError(_('Product QU > Product Available QTY in this location'))
            if rec.product_qty <= 0.0:
                raise ValidationError(_('Product QU Must be > 0.0'))
            if rec.product_serial_lines:
                if sum(rec.product_serial_lines.mapped('product_qty')) != rec.product_qty:
                    raise ValidationError(_('Total lines Quantities must equal requested quantity'))

    @api.depends('product_serial_lines')
    def _compute_lot_ids(self):
        for rec in self:
            rec.lot_ids = rec.product_serial_lines.mapped('lot_id') if rec.product_serial_lines else False

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id

    def action_assign_serials(self):
        view_id = self.env.ref('itq_sample_gift_request.sample_gift_line_form').id

        return {
            'name': _('Assign Product Lots/serials'),
            'type': 'ir.actions.act_window',
            'res_model': 'sample.gift.line',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'new',
        }

    def action_assign_product_serials(self):
        # self.lot_ids = self.product_serial_lines.mapped('lot_id')
        # print(self.lot_ids)
        return True
