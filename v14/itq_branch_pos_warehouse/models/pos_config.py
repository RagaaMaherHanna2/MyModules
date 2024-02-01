# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class POSConfig(models.Model):
    _inherit = 'pos.config'

    branch_is_set = fields.Boolean()
    image = fields.Binary(string='Image', compute='_compute_image')

    @api.depends('branch_id.image_1920')
    def _compute_image(self):
        for rec in self:
            if self.branch_id and self.branch_id.image_1920:
                rec.image = self.branch_id.image_1920
            else:
                rec.image = self.env.user.company_id.logo

    @api.model
    def create(self, vals):
        res = super(POSConfig, self).create(vals)
        self._check_pos_count_limit()
        return res

    def action_unarchive(self):
        self._check_pos_count_limit(unarchived=True)
        return super(POSConfig, self).action_unarchive()

    def _check_pos_count_limit(self, unarchived=False):
        current_pos_count = self.search_count([('branch_id', 'in', self.env.user.branch_ids.ids)])
        if unarchived:
            current_pos_count += 1
        branch_pos_limit = self.env['ir.config_parameter'].sudo().get_param(
            'itq_branch_pos_warehouse.pos_limit')
        if int(branch_pos_limit) != 0:
            if current_pos_count > int(branch_pos_limit):
                raise ValidationError(
                    _("You've exceeded your Account pos limit - Please contact your Administrator"))
        return True
