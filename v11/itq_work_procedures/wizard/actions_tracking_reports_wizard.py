# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.hijri_date_util.models import itq_date_util as Hijri


class ActionsTrackingReportsWizard(models.TransientModel):
    _name = 'actions.tracking.reports.wizard'
    _description = "Actions Tracking Reports Wizard"

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    group_by = fields.Selection([('user', 'المستخدم'),
                                 ('current_admin_unit', 'الوحدة الإدارية للمستخدم'), ], string='Group By',
                                default='user')

    order_by = fields.Selection([('action_date', 'تاريخ الحركة'),
                                 ('alphabetic', 'ترتب ابجدي'), ], string='Order By',
                                default='action_date')

    @api.constrains('date_from', 'date_to')
    def check_date_validations(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("Date from should be less than date to"))

    def _get_hijri_date(self, date):
        if date and isinstance(date, str):
            rec_date = datetime.strptime(date, '%Y-%m-%d')
            date = Hijri.create_hij_from_greg(rec_date)
        else:
            date = Hijri.create_hij_from_greg(date)
        return str(date.year) + "/" + str(date.month) + "/" + str(date.day)

    def get_report_order(self):
        self.ensure_one()
        order_by = self.order_by
        if order_by == 'action_date':
            order = 'action_date desc'
        else:
            order = 'procedure_name asc'
        return order

    def get_procedures_actions(self):
        self.ensure_one()
        order_by = self.get_report_order()
        domain = [
            ('action_date', '>=', self.date_from),
            ('action_date', '<=', self.date_to),
        ]
        actions = self.env['actions.tracking'].search(domain, order=order_by)
        return actions

    def print_actions_tracking_report(self):
        self.ensure_one()
        return self.env.ref('itq_work_procedures.print_procedures_actions_tracking_pdf').report_action(self)
