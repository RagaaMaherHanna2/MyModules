# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class NotificationSettings(models.Model):
    _name = 'notification.settings'
    _description = "Notification Settings"
    _rec_name = "notification_days"

    notification_days = fields.Integer(string='عدد الايام', required=True, default=3, )
    active_settings = fields.Boolean(default=True, string='نشط')

    @api.constrains('notification_days')
    def check_notification_days(self):
        for rec in self:
            if not 1 <= rec.notification_days <= 10:
                raise ValidationError(_('لابد ان تكون عدد الايام من 1 إلى 10 أيام!'))

    @api.constrains('active_settings')
    def check_active_constrains(self):
        for rec in self:
            if rec.active_settings and self.search([('active_settings', '=', True), ('id', '!=', rec.id), ]):
                raise ValidationError(_(' لابد ان يكون هناك سجل نشط واحد فقط لإعدادت الاشعارات!'))
