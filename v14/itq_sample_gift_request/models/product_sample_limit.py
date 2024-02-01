# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductSampleLimit(models.Model):
    _name = 'product.sample.limit'

    product_id = fields.Many2one('product.template', string='Product', ondelete='set null')
    product_product_id = fields.Many2one('product.product', string='Product Template', ondelete='set null')
    branch_id = fields.Many2one('res.branch')
    limit_qty = fields.Float('Limit Quantity')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom = fields.Many2one('uom.uom', string='Product UOM', required=True, )

    @api.constrains('limit_qty')
    def _constrains_limit_qty(self):
        for rec in self:
            if rec.limit_qty <= 0.0:
                raise ValidationError(_('Product limit Quantity Must be > 0.0'))

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id
