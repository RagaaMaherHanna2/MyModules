# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ActionsTracking(models.Model):
    _name = 'actions.tracking'
    _inherit = ['itq.wp.access']
    _description = "Actions Tracking"
    _rec_name = 'procedure_id'
    _unit_field_name = 'department_id'
    _procedure_availability_field_name = 'procedure_availability'

    user_id = fields.Many2one('res.users', string="Action User", required=1)
    action_date = fields.Datetime(string="Action Date")
    action_type = fields.Selection([
        ('view', 'عرض'),
        ('print', 'طباعه'),
        ('attachment_download', 'تنزيل ملف'),
    ], 'actions Type')
    procedure_id = fields.Many2one('work.procedure', ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Current Unit')
    procedure_availability = fields.Selection([('department_related', 'Department Related'),
                                               ('general', 'General'),
                                               ('secret', 'Secret')], string='Procedure Availability', )
    procedure_name = fields.Char(string='Name')
    procedure_code = fields.Char(string='Code')
    procedure_version_no = fields.Char(string='Version NO')
    attachment_name = fields.Char(string='Attachment Name')
    procedure_create_date = fields.Datetime(string='Creation Date')
    procedure_setting_side_department = fields.Char(string='Setting side')
    procedure_user = fields.Char(string='Procedure User')
