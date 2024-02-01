# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_limit = fields.Integer(string='POS Limitation',
                               config_parameter='itq_branch_pos_warehouse.pos_limit')
