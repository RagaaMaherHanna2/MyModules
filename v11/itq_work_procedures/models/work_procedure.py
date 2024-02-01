# -*- coding: utf-8 -*-
from datetime import datetime
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.hijri_date_util.models import itq_date_util as Hijri


class WorkProcedure(models.Model):
    _name = 'work.procedure'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'itq.wp.access']
    _description = "Work Procedure"
    _order = 'create_date desc'
    _parent_name = "parent_id"
    _unit_field_name = 'department_id'
    _procedure_availability_field_name = 'procedure_availability'

    @api.model
    def _default_get_review_department(self):
        return self.env['procedures.review.settings'].search([], limit=1).review_department_id

    code = fields.Char(readonly=True)
    name_id = fields.Many2one('procedure.name', string='Procedure Name', required=True, ondelete='restrict',
                              domain="[('name_active', '=', True)]")
    name = fields.Char(string="Procedure Name", track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user.id,
                              readonly=True,
                              required=True)
    latest_write_uid = fields.Many2one('res.users', string='مستخدم اخر تعديل', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department", required=True,
                                    domain=lambda self: self.env['itq.wp.access'].get_department_domain())
    scope_id = fields.Many2one('procedure.scope', string="Scope", required=True, domain="[('active_scope','=',True)]")
    procedure_label = fields.Char(readonly=True)
    parent_id = fields.Many2one('work.procedure', readonly=True)
    child_ids = fields.One2many('work.procedure', 'parent_id', string='Child Procedures')
    version_no = fields.Char(readonly=True)
    latest_version = fields.Boolean(default=True, readonly=True)
    procedure_availability = fields.Selection([('department_related', 'Department Related'),
                                               ('general', 'General'),
                                               ('secret', 'Secret')], string='Procedure Availability',
                                              default='department_related', required=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('under_review', 'Under Review'),
                              ('review_rejected', 'Review Rejected'),
                              ('under_confirmation', 'Under Confirmation'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected'),
                              ('archived', 'Archived')], string='State', default='draft')
    # More Details Page
    committee_members_ids = fields.Many2many('committee.member', string="Committee member",
                                             domain=lambda x: x.get_committee_members_domain(), required=True)
    version_reason = fields.Text(string="Reason", required=True)
    target = fields.Text(string="Target", required=True)
    allowed_departments = fields.Many2many('hr.department', compute='_compute_allowed_departments')
    responsibility_department_id = fields.Many2one('hr.department', string="Responsibility", required=True)
    setting_side_department_id = fields.Many2one('hr.department', string="Setting side", required=True)
    inputs = fields.Text(string="Inputs", required=True)
    outputs = fields.Text(string="Outputs", required=True)
    procedure_settings_criteria = fields.Html(string="Settings Criteria", required=True)
    file_name = fields.Char(string='Flowchart File')
    flowchart_file = fields.Binary(string='Flowchart File', attachment=True)
    procedure_request_review_date = fields.Date('تاريخ إرسال للمراجعه', readonly=True)
    procedure_review_date = fields.Date('تاريخ إرسال للإعتماد', readonly=True)
    next_procedure_review_date = fields.Date(string='Next Procedure Review Date')
    procedure_confirmation_date = fields.Date('تاريخ الاعتماد', readonly=True)

    procedure_execution_days = fields.Integer(string='الزمن الكلي لتنفيذ الاجراء', compute='_compute_execution_time')
    procedure_execution_hours = fields.Integer(string='Execution Hours', compute='_compute_execution_time')
    procedure_execution_mints = fields.Integer(string='Execution Mints', compute='_compute_execution_time')

    # Procedure Steps
    procedure_step_ids = fields.One2many('procedure.step', 'procedure_id', string='Steps And Events')

    # Related Procedures
    related_procedure_ids = fields.One2many('related.work.procedure', 'procedure_id', string='Related Procedures')

    # Procedure Resource
    procedure_resource_ids = fields.One2many('procedure.resource', 'procedure_id', string='Procedure Resources')

    # Procedure Documents
    procedure_doc_ids = fields.One2many('procedure.document', 'procedure_id', string='Procedure Documents')

    # Procedures Approvals
    approvals_tracking_ids = fields.One2many('approval.tracking.line', 'procedure_id', string='Approvals Tracking')

    # Helper Fields
    company_id = fields.Many2one('res.company', string='Company', )
    procedure_review_user_id = fields.Many2one('res.users', string='Procedure Reviewer',
                                               compute='_compute_procedure_approval_users')
    latest_procedure_review_user_id = fields.Many2one('res.users', string='Latest Procedure Reviewer')
    procedure_review_department_id = fields.Many2one('hr.department', string='Procedure Review Department',
                                                     default=_default_get_review_department)
    procedure_confirm_user_id = fields.Many2one('res.users', string='Procedure Confirm',
                                                compute='_compute_procedure_approval_users')
    latest_procedure_confirm_user_id = fields.Many2one('res.users', string='Latest Procedure Confirm')
    procedure_confirm_department_id = fields.Many2one('hr.department', string='Procedure Review Department',
                                                      compute='_compute_procedure_approval_users')

    can_request_approve = fields.Boolean(compute='_compute_can_request_approve')
    can_add_new_v = fields.Boolean(compute='_compute_can_request_approve')
    can_review = fields.Boolean(compute='_compute_who_can_review')
    can_confirm = fields.Boolean(compute='_compute_who_can_confirm')
    can_archive = fields.Boolean(compute='_compute_who_can_confirm')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Cannot delete a Procedures that is not draft'))
        super(WorkProcedure, self).unlink()

    @api.model
    def create(self, vals):
        if 'version_no' not in vals:
            vals['version_no'] = '1.0'

        if 'parent_id' not in vals:
            code = self.env['ir.sequence'].next_by_code('work.procedure.seq')
            vals['code'] = self.env['hr.department'].browse(vals['department_id']).code + '-' + code

        if 'name_id' in vals:
            vals['name'] = self.env['procedure.name'].browse(vals['name_id']).name

        return super(WorkProcedure, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'message_follower_ids' not in vals:
                vals['latest_write_uid'] = rec.env.user.id
            res = super(WorkProcedure, self).write(vals)
            old_code = rec.code.split('-')[1]
            if 'department_id' in vals:
                rec.code = rec.department_id.code + '-' + old_code
            return res

    @api.constrains('name_id', 'department_id')
    def _name_id_department_id_constrains(self):
        for rec in self:
            if rec.name_id and rec.scope_id:
                rec_parents = self.search(['|', ('id', 'parent_of', rec.id), ('id', 'parent_of', rec.parent_id.id)])
                if self.search([('name_id', '=', rec.name_id.id),
                                ('department_id', '=', rec.department_id.id),
                                ('id', '!=', rec.id),
                                ('id', 'not in', rec_parents.ids)]):
                    raise ValidationError(_('This Procedure Name has been registered with this department before.'))

    @api.constrains('next_procedure_review_date')
    def _next_procedure_review_date_constrains(self):
        for rec in self:
            if rec.next_procedure_review_date:
                next_procedure_review_date = datetime.strptime(rec.next_procedure_review_date, '%Y-%m-%d').date()
                if next_procedure_review_date:
                    if next_procedure_review_date < fields.date.today():
                        raise ValidationError(_('you have to choose upcoming date'))

    @api.constrains('procedure_settings_criteria')
    def _procedure_settings_criteria_constrains(self):
        for rec in self:
            clean = re.compile('<.*?>')
            plan_text = re.sub(clean, '', rec.procedure_settings_criteria)
            if not plan_text.strip():
                raise ValidationError(_('لابد من إضافة معايير وضبط الإجراء'))

    @api.constrains('procedure_step_ids')
    def _check_execution_time(self):
        for rec in self:
            if rec.procedure_step_ids:
                for step in rec.procedure_step_ids:
                    if sum([step.execution_days, step.execution_hours, step.execution_mints]) <= 0:
                        raise ValidationError(_("For step %s Please Enter Execution Time") % step.name)
                    if not (0 <= step.execution_hours <= 24):
                        raise ValidationError(_("For step %s Execution hours must be less than 24") % step.name)
                    if not (0 <= step.execution_mints <= 60):
                        raise ValidationError(_("For step %s Execution mints must be less than 60") % step.name)

    @api.depends('procedure_step_ids')
    def _compute_execution_time(self):
        days = hours = mints = 0.0
        for rec in self:
            if rec.procedure_step_ids:
                days = sum(rec.procedure_step_ids.mapped('execution_days'))
                hours = sum(rec.procedure_step_ids.mapped('execution_hours'))
                mints = sum(rec.procedure_step_ids.mapped('execution_mints'))
            rec.procedure_execution_days = days
            rec.procedure_execution_hours = hours
            rec.procedure_execution_mints = mints

    @api.depends('state', 'user_id')
    def _compute_can_request_approve(self):
        can_request_approve = can_add_new_v = False
        for rec in self:
            if self.env.user == rec.user_id:
                if rec.state in ['draft', 'review_rejected', 'rejected']:
                    can_request_approve = True
                if rec.state == 'confirmed' and rec.latest_version:
                    can_add_new_v = True
            rec.can_request_approve = can_request_approve
            rec.can_add_new_v = can_add_new_v

    @api.depends('state', 'procedure_review_user_id')
    def _compute_who_can_review(self):
        can_review = False
        for rec in self:
            if rec.state == 'under_review' and rec.procedure_review_user_id:
                if self.env.user == rec.procedure_review_user_id:
                    can_review = True
            rec.can_review = can_review

    @api.depends('state', 'procedure_confirm_user_id')
    def _compute_who_can_confirm(self):
        can_confirm = False
        can_archive = False
        for rec in self:
            if rec.procedure_confirm_user_id and self.env.user == rec.procedure_confirm_user_id:
                if rec.state == 'under_confirmation':
                    can_confirm = True
                if rec.state == 'confirmed':
                    can_archive = True
            rec.can_confirm = can_confirm
            rec.can_archive = can_archive

    @api.depends('department_id')
    def _compute_procedure_approval_users(self):
        for rec in self:
            procedure_confirm_user_id = procedure_review_user_id = procedure_confirm_department_id = False
            if rec.department_id:
                review_config = self.env['procedures.review.settings'].search(
                    ['|', ('review_department_id', '=', rec.department_id.id),
                     ('review_department_units_ids', 'in', rec.department_id.id)])
                if review_config:
                    procedure_review_user_id = review_config.review_user_id

                confirm_config = self.env['procedures.confirm.settings'].search(
                    ['|', ('confirm_department_units_ids', 'in', rec.department_id.id),
                     ('confirm_department_id', '=', rec.department_id.id)])
                if confirm_config:
                    procedure_confirm_user_id = confirm_config.confirm_user_id
                    procedure_confirm_department_id = confirm_config.confirm_department_id
            rec.procedure_confirm_user_id = procedure_confirm_user_id
            rec.procedure_confirm_department_id = procedure_confirm_department_id
            rec.procedure_review_user_id = procedure_review_user_id

    @api.depends('department_id')
    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.responsibility_department_id = self.setting_side_department_id = False
            sub_admin_units = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                self.department_id)
            if sub_admin_units:
                return {'domain': {'responsibility_department_id': [('id', 'in', sub_admin_units)],
                                   'setting_side_department_id': [('id', 'in', sub_admin_units)]}}

    @api.depends('department_id')
    def _compute_allowed_departments(self):
        sub_admin_units = []
        for rec in self:
            if rec.department_id:
                sub_admin_units = self.env['hr.department.group'].get_current_and_recursive_sub_admin_unit_ids(
                    rec.department_id)
            rec.allowed_departments = sub_admin_units

    def get_committee_members_domain(self):
        active_committee_members = False
        active_documentation_committee = self.env['documentation.committee'].search([('active_committee', '=', True)],
                                                                                    limit=1)
        if active_documentation_committee:
            active_committee_members = active_documentation_committee.member_ids.filtered(
                lambda member: member.active_member).ids
        return [('id', 'in', active_committee_members)]

    def get_allowed_procedures(self, state=False):
        self.ensure_one()
        allowed_procedures = self.search([('state', '=', state)])
        if state == 'under_review':
            allowed_procedures = allowed_procedures.filtered(
                lambda p: p.procedure_review_user_id.id == self.env.user.id)
        elif state == 'under_confirmation':
            allowed_procedures = allowed_procedures.filtered(
                lambda p: p.procedure_confirm_user_id.id == self.env.user.id)
        return allowed_procedures

    def action_my_work_procedures(self, state=None, action_name='دليل إجراءات العمل'):
        self.ensure_one()
        form_view_id = self.env.ref('itq_work_procedures.work_procedure_view_form').id
        tree_view_id = self.env.ref('itq_work_procedures.work_procedure_view_tree').id
        ctx = {'create': False, 'edit': False}
        my_procedures = self.get_allowed_procedures(state=state)

        return {
            'name': action_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'work.procedure',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', my_procedures.ids)],
            'context': ctx,
        }

    def action_request_review(self):
        for record in self:
            if not record.procedure_review_user_id:
                raise ValidationError(
                    _("There's no reviewer please contact your admin system to add the procedure reviewer"))

            notification_data = [{'notified_user': record.procedure_review_user_id,
                                  'notification_note': 'هذا الإجراء فى إنتظار المراجعه'}]
            self.env['manage.notifications'].create_notification(notification_data, record, subject='Procedure Under '
                                                                                                    'Review')
            record.procedure_request_review_date = fields.Date.today()

            if record.state in ['review_rejected', 'rejected']:
                new_version = round(float(record.version_no) + 0.1, 1)
                record.version_no = str(new_version)
            record.state = 'under_review'

    def action_archive(self):
        view_id = self.env.ref('itq_work_procedures.archive_warning_wizard_form').id
        return {
            'name': 'تحذير',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'archive.warning.wizard',
            'view_id': view_id,
            'target': 'new',
        }

    def action_new_version(self):
        self.ensure_one()
        new_version = round(float(self.version_no) + 0.1, 1)
        self.latest_version = False
        self.ensure_one()
        parent_id = self.id
        if self.parent_id:
            parent_id = self.parent_id.id
        view_id = self.env.ref('itq_work_procedures.work_procedure_view_form').id
        new_version_fields = {
            'name': (self.name_id.name.split('-'))[0] + ' - ' + str(new_version),
            'version_no': str(new_version),
            'code': self.code,
            'parent_id': parent_id,
            'latest_version': True,
            'next_procedure_review_date': False,
        }
        new_version = self.copy(new_version_fields)
        for step in self.procedure_step_ids:
            step.copy({'procedure_id': new_version.id})
        for procedure in self.related_procedure_ids:
            procedure.copy({'procedure_id': new_version.id})
        for resource in self.procedure_resource_ids:
            resource.copy({'procedure_id': new_version.id})
        for doc in self.procedure_doc_ids:
            doc.copy({'procedure_id': new_version.id})

        new_version.action_create_actions_tracking(action_type='view')

        return {
            'name': 'تعريف دليل إجراءات العمل',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'work.procedure',
            'view_id': view_id,
            'target': 'current',
            'res_id': new_version.id,
        }

    def action_create_actions_tracking(self, action_type, attachment_name=''):
        for rec in self:
            self.env['actions.tracking'].create({
                'procedure_id': rec.id,
                'department_id': rec.department_id.id,
                'procedure_availability': rec.procedure_availability,
                'procedure_name': rec.name,
                'procedure_code': rec.code,
                'procedure_create_date': rec.create_date,
                'procedure_setting_side_department': rec.setting_side_department_id.name,
                'procedure_user': rec.user_id.name,
                'procedure_version_no': rec.version_no,

                'user_id': self.env.user.id,

                'action_date': fields.Datetime.now(),
                'action_type': action_type,
                'attachment_name': attachment_name,
            })

    def _get_hijri_date(self, date):
        if date and isinstance(date, str):
            rec_date = datetime.strptime(date, '%Y-%m-%d')
            date = Hijri.create_hij_from_greg(rec_date)
        else:
            date = Hijri.create_hij_from_greg(date)
        return str(date.year) + "/" + str(date.month) + "/" + str(date.day)
