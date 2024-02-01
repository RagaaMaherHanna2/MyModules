# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.hijri_date_util.models import itq_date_util as Hijri


class ProcedureReportsWizard(models.TransientModel):
    _name = 'procedure.reports.wizard'
    _description = "Procedure Reports Wizard"

    def _get_order_selections(self):
        report_for = self.env.context.get('default_report_for')
        selections = [('alphabetic', 'أبجدى'), ]
        if report_for == 'under_review':
            selections.append(('request_review_date', 'تاريخ إرسال للمراجعه'))
        elif report_for == 'under_confirmation':
            selections.append(('review_date', 'تاريخ المراجعه'))
            selections.append(('request_review_date', 'تاريخ إرسال للمراجعه'))
        else:
            selections.append(('confirm_date', 'تاريخ الاعتماد'))
        return selections

    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    group_by = fields.Selection([('department', 'الاداره'),
                                 ('scope', 'النطاق'), ], string='Group By', default='department')

    order_by = fields.Selection(lambda self: self._get_order_selections(),
                                string='Order By', default='alphabetic')
    department_ids = fields.Many2many('hr.department', string="Department", )
    scope_ids = fields.Many2many('procedure.scope', string="Scope", domain="[('active_scope','=',True)]")
    latest_v = fields.Boolean(string='Latest Version', )
    allowed_procedure_ids = fields.Many2many('work.procedure', string='الاجراء',
                                             compute='_get_allowed_allowed_procedures')
    procedure_ids = fields.Many2many('work.procedure', string='الاجراء', )

    report_for = fields.Selection([('under_review', 'Under Review'),
                                   ('under_confirmation', 'Under Confirmation'),
                                   ('confirmed', 'Confirmed'),
                                   ('statistical', 'Statistical report'),
                                   ], string='State')
    allow_general_procedure = fields.Boolean('Print all General Procedures?')
    general_department_ids = fields.Many2many('hr.department', 'itq_general_department_id_general_department_id_rel',
                                              'itq_general_department_id', 'general_department_id',
                                              string="General Departments")
    allow_departments_procedure = fields.Boolean('Print Related Department Procedures?')
    related_department_ids = fields.Many2many('hr.department', string="Related Departments",
                                              domain=lambda self: self.env['itq.wp.access'].get_department_domain())
    all_selected_departments = fields.Many2many('hr.department', string="All Departments",
                                                compute='_compute_all_selected_departments')

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.date_to or self.date_from:
            self.procedure_ids = False

    @api.constrains('date_from', 'date_to')
    def check_date_validations(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("Date from should be less than date to"))

    @api.constrains('latest_v', 'allow_general_procedure', 'allow_departments_procedure')
    def check_departments_options(self):
        for rec in self:
            if rec.latest_v and not (rec.allow_general_procedure or rec.allow_departments_procedure):
                raise ValidationError(_("You have to choose at least one option!"))

    @api.depends('latest_v', 'date_from', 'date_to')
    def _get_allowed_allowed_procedures(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.report_for == 'confirmed':
                domain = [
                    ('state', '=', 'confirmed')]
                if rec.date_from:
                    domain.append(('create_date', '>=', rec.date_from))
                if rec.date_to:
                    domain.append(('create_date', '<=', rec.date_to))
            if rec.latest_v:
                domain.append(('latest_version', '=', True))
            rec.allowed_procedure_ids = self.env['work.procedure'].with_context(
                allow_general_procedure_availability=rec.allow_general_procedure).search(domain)

    @api.depends('general_department_ids', 'general_department_ids')
    def _compute_all_selected_departments(self):
        for rec in self:
            rec.all_selected_departments = rec.related_department_ids | rec.general_department_ids if rec.related_department_ids or rec.general_department_ids else False

    def _get_hijri_date(self, date):
        if date and isinstance(date, str):
            rec_date = datetime.strptime(date, '%Y-%m-%d')
            date = Hijri.create_hij_from_greg(rec_date)
        else:
            date = Hijri.create_hij_from_greg(date)
        return str(date.year) + "/" + str(date.month) + "/" + str(date.day)

    def get_report_title(self):
        self.ensure_one()
        if self.report_for == 'under_review':
            report_title = 'تقرير الاجراءات تحت المراجعه'
        elif self.report_for == 'under_confirmation':
            report_title = 'تقرير الاجراءات تحت الإعتماد'
        elif self.report_for == 'confirmed':
            if self.latest_v:
                report_title = 'تقرير دليل الاجراءات المعتمده'
            else:
                report_title = 'تقرير الاجراءات المعتمده'
        else:
            report_title = 'تقرير احصائي '
            if self.date_from:
                report_title += 'عن فترة من تاريخ  %s ' % self.date_from
            if self.date_to:
                report_title += 'الي تاريخ  %s ' % self.date_to
        return report_title

    def get_report_order(self):
        self.ensure_one()
        order_by = self.order_by
        if order_by == 'request_review_date':
            order = 'procedure_request_review_date desc'
        elif order_by == 'review_date':
            order = 'procedure_review_date desc'
        elif order_by == 'confirm_date':
            order = 'procedure_confirmation_date desc'
        else:
            order = 'name asc'
        return order

    def get_procedures(self):
        order_by = self.get_report_order()
        procedures = related_procedures = self.env['work.procedure']
        domain = []
        ctx = {}
        if self.latest_v:
            domain.extend([('state', '=', 'confirmed'), ('latest_version', '=', True)])
            if self.allow_general_procedure:
                ctx.update({'allow_general_procedure_availability': True})
                procedures |= procedures.with_context(ctx).search(domain, order=order_by).filtered(
                    lambda p: p.procedure_availability in ['general', 'secret'])
                if self.general_department_ids:
                    procedures = procedures.filtered(lambda p: p.department_id.id in self.general_department_ids.ids)
            if self.allow_departments_procedure:
                related_procedures = related_procedures.search(domain, order=order_by).filtered(
                    lambda p: p.procedure_availability in ['department_related', 'secret'])
                if self.related_department_ids:
                    related_procedures = related_procedures.filtered(
                        lambda p: p.department_id.id in self.related_department_ids.ids)
            print(self.all_selected_departments)

            procedures |= related_procedures
        else:
            if self.date_from:
                domain.append(('create_date', '>=', self.date_from))
            if self.date_from:
                domain.append(('create_date', '<=', self.date_to))
            if self.report_for == 'confirmed':
                if self.procedure_ids:
                    domain = [
                        ('id', '=', self.procedure_ids.ids)
                    ]
                else:
                    domain.append(('state', '=', 'confirmed'))
            elif self.report_for == 'statistical':
                ctx.update({'allow_general_procedure_availability': True})
                if self.department_ids:
                    domain.append(('department_id', 'in', self.department_ids.ids))
                if self.scope_ids:
                    domain.append(('scope_id', 'in', self.scope_ids.ids))
            else:
                domain.append(('state', '=', self.report_for))

            procedures = self.env['work.procedure'].with_context(ctx).search(domain, order=order_by)
        return procedures

    def action_view_procedures(self):
        self.ensure_one()
        action = self.env.ref('itq_work_procedures.action_my_procedure').read()[0]
        action['context'] = {'create': 0, 'edit': 0}
        action['domain'] = [('id', 'in', self.get_procedures().ids)]
        return action
