# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductSerialLine(models.Model):
    _name = 'product.serial.line'
    _description = 'Product Serial Line'
    _rec_name = 'product_id'

    sample_line_id = fields.Many2one('sample.gift.line', string='Sample Line', )
    product_id = fields.Many2one(related='sample_line_id.product_id', string='Product', )
    company_id = fields.Many2one(related='sample_line_id.company_id', string='Company', )
    product_uom = fields.Many2one(related='sample_line_id.product_uom', string='Product UOM', )
    product_qty = fields.Float('Quantity')
    lot_id = fields.Many2one('stock.production.lot', string='Lots/Serial',
                             domain="[('product_id', '=', product_id)]", required=True)

    @api.constrains('product_qty')
    def _constrains_product_qty(self):
        for rec in self:
            if rec.product_qty <= 0.0:
                raise ValidationError(_('Product %s QU Must be > 0.0' % rec.name))
            if rec.product_id.tracking == 'serial':
                if rec.product_qty != 1.0:
                    raise ValidationError(_('quantity must be 1 because Product is tracking by unique serial!'))
                if rec.env['stock.move.line'].search([('product_id', '=', rec.product_id.id),
                                                      ('lot_id', '=', rec.lot_id.id)]):
                    raise ValidationError(_('this serial is used and Product serial Must be unique!'))
