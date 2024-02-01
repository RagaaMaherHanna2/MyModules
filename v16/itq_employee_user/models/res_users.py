# -*- coding: utf-8 -*-

from odoo import api, models


class User(models.Model):
    _inherit = 'res.users'

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'create_employee' not in default:
            default['create_employee'] = True
        return super(User, self).copy(default=default)
