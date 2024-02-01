# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ApprovalTrackingLine(models.Model):
    _name = 'approval.tracking.line'
    _description = "Approval Tracking Line"

    sequence = fields.Char(string="Sequence", compute='_sequence_ref')
    procedure_id = fields.Many2one('work.procedure')
    activity_id = fields.Many2one('mail.activity')

    approver_id = fields.Many2one('res.users', string="Approver", default=lambda self: self.env.user.id)
    action_date = fields.Datetime(string="Action Date")
    state = fields.Char('Approval State')
    current_version_no = fields.Char('Current Version NO')

    notes = fields.Text('Notes')
    rejection_reasons = fields.Text('Rejection Reasons')
    approval_doc_ids = fields.One2many('procedure.document', 'approval_id', string='Examples Files')

    @api.model
    def create(self, vals):
        notification_data = []
        subject = ''
        active_procedure = self.env['work.procedure'].browse(self._context['active_id'])
        data_to_write = {}
        if self.env.context.get('action') == 'review_approve':
            notification_data = [{'notified_user': active_procedure.procedure_confirm_user_id,
                                  'notification_note': _('Need Your confirmation')},
                                 {'notified_user': active_procedure.user_id,
                                  'notification_note': _('Your procedure approved review from reviewer and waiting for '
                                                         'confirmation')}]
            vals['state'] = subject = _('Review Approved')
            data_to_write = {
                'procedure_review_date': fields.Date.today(),
                'latest_procedure_review_user_id': self.env.user.id,
                'state': 'under_confirmation'
            }

        elif self.env.context.get('action') == 'review_reject':
            notification_data = [{'notified_user': active_procedure.user_id,
                                  'notification_note': _('Your procedure rejected by reviewer check reasons')}]
            vals['state'] = subject = _('Review Rejected')
            data_to_write = {
                'latest_procedure_review_user_id': self.env.user.id,
                'state': 'review_rejected',
            }
        elif self.env.context.get('action') == 'confirm':
            notification_data = [{'notified_user': active_procedure.user_id,
                                  'notification_note': _('Work Procedure is Confirmed')},
                                 {'notified_user': active_procedure.procedure_review_user_id,
                                  'notification_note': _('Work Procedure is Confirmed')}]
            vals['state'] = subject = _('Confirmed')
            data_to_write = {
                'procedure_confirmation_date': fields.Date.today(),
                'latest_procedure_confirm_user_id': self.env.user.id,
                'state': 'confirmed',
            }

        elif self.env.context.get('action') == 'reject':
            notification_data = [{'notified_user': active_procedure.user_id,
                                  'notification_note': _('Work Procedure rejected check reasons')},
                                 {'notified_user': active_procedure.procedure_review_user_id,
                                  'notification_note': _('Work Procedure rejected check reasons')}]
            vals['state'] = subject = _('Rejected')
            data_to_write = {
                'latest_procedure_confirm_user_id': self.env.user.id,
                'state': 'rejected',
            }
        self.env['manage.notifications'].create_notification(notification_data, active_procedure,
                                                             subject=subject)
        active_procedure.write(data_to_write)

        vals['action_date'] = fields.Datetime.now()
        vals['current_version_no'] = active_procedure.version_no

        return super(ApprovalTrackingLine, self).create(vals)

    @api.depends('procedure_id.approvals_tracking_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.procedure_id.approvals_tracking_ids:
                no += 1
                l.sequence = no
