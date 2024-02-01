# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ManageNotifications(models.AbstractModel):
    _name = 'manage.notifications'
    _description = "Manage Notifications"

    def create_notification(self, notification_data, res_id, subject=''):
        for data in notification_data:
            notified_user = data['notified_user']
            if res_id in self.env['work.procedure'].sudo(notified_user.id).search([]):
                res_id.message_post(
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    subject=subject,
                    body=data['notification_note'],
                    res_id=res_id.id,
                    author_id=self.env.user.partner_id.id,
                    partner_ids=[notified_user.partner_id.id])

    def review_procedures_notifications(self):
        self.ensure_one()
        notification_days = self.env['notification.settings'].search([('active_settings', '=', True)],
                                                                     limit=1).notification_days
        if notification_days:
            nex_procedures_to_review = self.env['work.procedure'].search([('state', 'in', ['draft', 'under_review']),
                                                                          ('next_procedure_review_date', '=',
                                                                           date.today() + timedelta(
                                                                               days=notification_days))])
            if nex_procedures_to_review:
                for procedure in nex_procedures_to_review:
                    notification_data = [{'notified_user': procedure.user_id,
                                          'notification_note': _(
                                              'سيتم مراجعة هذا الاجراء بعد %s أيام') % notification_days}, ]
                    self.create_notification(notification_data, procedure, subject='procedure will be reviewed')
