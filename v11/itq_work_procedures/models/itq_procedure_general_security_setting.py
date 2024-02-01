# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItqProcedureGeneralSecuritySetting(models.Model):
    _name = 'itq.procedure.general.security.setting'

    name = fields.Char(string='Group', required=True)
    is_admin = fields.Boolean(string='Admin Security', default=False, track_visibility='onchange')
    access_secrets = fields.Boolean(string='Can Access Secret Procedures', default=False, track_visibility='onchange')
    admin_unit_ids = fields.Many2many('hr.department', 'itq_procedure_security_id_admin_unit_id_rel',
                                      'itq_procedure_security_id', 'admin_unit_id', required=True)
    user_ids = fields.Many2many('res.users', 'itq_procedure_security_id_user_id_rel',
                                'itq_procedure_security_id', 'user_id', required=True)
    rank_ids = False
    module_categ_ids = False
    user_name = False

    def action_units_children(self):
        self.ensure_one()
        return {
            'name': _('Add / Delete Units Children'),
            'type': 'ir.actions.act_window',
            'res_model': 'itq.unit.setting.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    @api.constrains('is_admin', 'admin_unit_ids', 'user_ids')
    def check_data_in_record(self):
        for rec in self:
            if not rec.user_ids:
                raise ValidationError(_("Please enter users"))
            if not rec.is_admin and not rec.admin_unit_ids:
                raise ValidationError(_("Please enter admin unit"))
