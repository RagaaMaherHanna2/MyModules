# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sample_limit_ids = fields.One2many('product.sample.limit', 'product_id', 'Monthly Sample/Gift Limit', )
    branches_ids = fields.Many2many('res.branch', compute='_compute_branches_ids')

    @api.depends('sample_limit_ids', 'sample_limit_ids.product_id')
    def _compute_branches_ids(self):
        for rec in self:
            branches_ids = self.env.user.branch_ids
            if rec.sample_limit_ids:
                branches_ids = branches_ids - rec.sample_limit_ids.mapped('branch_id')
            rec.branches_ids = branches_ids


class ProductProduct(models.Model):
    _inherit = 'product.product'

    variant_sample_limit_ids = fields.One2many('product.sample.limit', 'product_product_id', 'Monthly Sample/Gift Limit', )
    branches_ids = fields.Many2many('res.branch', compute='_compute_branches_ids')

    @api.depends('sample_limit_ids', 'sample_limit_ids.product_product_id')
    def _compute_branches_ids(self):
        for rec in self:
            branches_ids = self.env.user.branch_ids
            if rec.sample_limit_ids:
                branches_ids = branches_ids - rec.sample_limit_ids.mapped('branch_id')
            rec.branches_ids = branches_ids

    @api.model
    def create(self, vals):
        print(vals)
        if 'sample_limit_ids' in vals:
            print(vals['sample_limit_ids'])
        if 'product_tmpl_id' in vals:
            print(vals['product_tmpl_id'])

        return super(ProductProduct, self).create(vals)
