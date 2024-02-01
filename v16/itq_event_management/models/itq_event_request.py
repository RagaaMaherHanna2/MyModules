from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from lxml import etree
import json
import pytz


class EventRequest(models.Model):
    _name = "itq.event.request"
    _inherit = ['mail.thread', 'itq.abstract.validate.field.format']
    _description = _('Event Request')

    request_number = fields.Char(readonly=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('under_review', 'Under Review'),
                              ('under_approve', 'Under Approve'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected')],
                             required=True,
                             default='draft', readonly=True, tracking=True)
    request_date = fields.Datetime(default=lambda self: datetime.now(), readonly=True, tracking=True)
    # Requester Department group
    requester_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, readonly=True,
                                   ondelete='restrict', tracking=True)

    department_id = fields.Many2one('hr.department', default=lambda self: self.env.user.employee_id.department_id,
                                    readonly=True, ondelete='restrict', tracking=True)
    department_manager_id = fields.Many2one('hr.employee', default=lambda
        self: self.env.user.employee_id.department_id.manager_id, readonly=True, ondelete='restrict', tracking=True)
    contact_number = fields.Char(default=lambda self: self.env.user.employee_id.work_phone, required=True,
                                 tracking=True)
    contact_email = fields.Char(default=lambda self: self.env.user.employee_id.work_email, required=True, tracking=True)

    # Event Data group
    name = fields.Char(required=True, tracking=True, string="Title")
    calendar_name = fields.Char(compute='_compute_calendar_name')
    event_goal = fields.Html(required=True, tracking=True)
    event_type_id = fields.Many2one('itq.event.type', required=True, ondelete='cascade', tracking=True,
                                    domain=[('state', '=', 'active')])
    event_date = fields.Datetime(required=True, default=lambda self: datetime.now(), tracking=True,
                                 string="Event Start Date")
    event_date_end = fields.Datetime(compute='_compute_event_date_end')

    event_number_of_days = fields.Integer(required=True, tracking=True)
    event_attraction_id = fields.Many2one('itq.attraction.location', required=True, ondelete='restrict', tracking=True,
                                          domain=[('state', '=', 'active')])
    other_event_attraction = fields.Char(tracking=True)
    is_other_attraction = fields.Boolean(compute='_compute_is_others')
    rehearsal_date = fields.Datetime(tracking=True)
    budget = fields.Selection(
        selection=[
            ('direct', 'Direct'),
            ('purchase_order', 'Purchase Order'),
            ('advance_payment', 'Advance Payment'),
            ('other', 'Other'),
        ], tracking=True)

    # Audience group
    target_audience_ids = fields.Many2many('itq.target.audience', required=True, tracking=True,
                                           domain="[('state', '=', 'active')]")
    expected_number_of_guests = fields.Integer(required=True, tracking=True)
    internal_guest_count = fields.Integer(tracking=True)
    external_guest_count = fields.Integer(tracking=True)
    guest_list = fields.Many2many('ir.attachment', 'guest_list_attachment_rel', tracking=True)

    # Guest Responsible group
    guest_responsible_name = fields.Char(required=True, string="Name", tracking=True)
    guest_responsible_mobile = fields.Char(required=True, string="Mobile", tracking=True)
    guest_responsible_phone = fields.Char(string="Phone", tracking=True)

    # Details Tabs
    event_program_attachment_ids = fields.Many2many('ir.attachment', 'event_program_attachment_rel', tracking=True)
    event_program_line_ids = fields.One2many('itq.event.program.line', 'event_request_id',
                                             tracking=True)
    guest_honor_ids = fields.One2many('itq.guest.honor', 'event_request_id', tracking=True)
    speaker_guest_ids = fields.One2many('itq.speaker.guest', 'event_request_id', tracking=True)
    amenity_specification_line_ids = fields.One2many('itq.amenity.specification.line', 'event_request_id',
                                                     default=lambda self: self.add_mandatory_amenities(), tracking=True)
    catering_type_line_ids = fields.One2many('itq.catering.type.line', 'event_request_id',
                                             default=lambda self: self.add_mandatory_catering(), tracking=True)
    return_reason = fields.Text(readonly=True, tracking=True)
    rejection_reason = fields.Text(readonly=True, tracking=True)
    used_amenity_specification_ids = fields.Many2many('itq.amenity.specification',
                                                      compute="compute_used_amenity_specification_ids")
    used_catering_type_ids = fields.Many2many('itq.catering.type',
                                              compute="compute_used_catering_type_ids")
    # Organizer Team
    organizer_team = fields.Selection(
        selection=[
            ('event_agency', 'Event Agency'),
            ('public_relation_department', 'Public Relation Department'),
        ],
        tracking=True,
    )
    organizer_name = fields.Char(string="Organizer Name", tracking=True)
    organizer_phone = fields.Char(string="Phone", tracking=True)
    organizer_mobile = fields.Char(string="Mobile", tracking=True)
    organizer_email = fields.Char(string="Email", tracking=True)
    team_member_ids = fields.One2many('itq.organizer.team', 'event_request_id', tracking=True)

    # Permissions
    event_permission_ids = fields.One2many('itq.event.permission', 'event_request_id', tracking=True)

    # Invitees Tab
    invitee_ids = fields.One2many('itq.invitee', 'event_request_id', tracking=True)
    is_ended_event = fields.Boolean(compute='_compute_event_date_end')

    def download_excel_button(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_custom_excel',
            'target': 'new',
        }

    @api.depends('event_attraction_id')
    def _compute_is_others(self):
        for record in self:
            if record.event_attraction_id == self.env.ref('itq_event_management.other_attraction_location'):
                record.is_other_attraction = True
            else:
                record.is_other_attraction = False

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'event.request.sequence')], limit=1)
        vals['request_number'] = sequence.next_by_id()
        res = super(EventRequest, self).create(vals)
        if res.guest_list:
            self.set_public_attachment(res.guest_list)
        if res.event_program_attachment_ids:
            self.set_public_attachment(res.event_program_attachment_ids)
        return res

    def write(self, vals):
        res = super(EventRequest, self).write(vals)
        if vals:
            if vals.get('guest_list'):
                self.set_public_attachment(self.mapped('guest_list'))
            if vals.get('event_program_attachment_ids'):
                self.set_public_attachment(self.mapped('event_program_attachment_ids'))
        return res

    @api.model
    def set_public_attachment(self, attachments):
        attachments.write({'public': True})

    def to_under_review(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("state must be draft"))
        self.constraint_event_date()
        if self.return_reason:
            self.send_under_review()
        else:
            return {
                'name': _('Event Instructions'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'itq.event.instruction.wizard',
                'target': 'new',
                'context': {'default_event_request_id': self.id, 'default_event_instructions': self.env.ref(
                    "itq_event_management.itq_event_management_settings_data").event_instructions},
            }

    def send_under_review(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("state must be draft"))
        self.constraint_event_date()
        self.write({'state': 'under_review', 'return_reason': False})
        self.send_notification_to_department_manager_id()

    def to_under_approve(self):
        self.ensure_one()
        if self.state != 'under_review':
            raise ValidationError(_("State must be Under Review"))
        self.write({'state': 'under_approve'})
        self.send_notification_to_creator()
        action = self.env["ir.actions.actions"]._for_xml_id("itq_event_management.itq_event_request_review_action")
        action['target'] = 'main'
        return action

    def to_return(self):
        self.ensure_one()
        if self.state not in ['under_approve', 'under_review']:
            raise ValidationError(_("State must be Under Review Or Under Approve"))
        action = self.env["ir.actions.actions"]._for_xml_id("itq_event_management.itq_event_request_review_action")
        if self.state == 'under_approve':
            action = self.env["ir.actions.actions"]._for_xml_id(
                "itq_event_management.itq_event_request_approve_action")
        self.state = 'draft'
        self.send_notification_to_creator()
        action['target'] = 'main'
        return action

    def to_reject(self):
        self.ensure_one()
        if self.state not in ['under_review', 'under_approve']:
            raise ValidationError(_("State must be Under Review Or Under Approve"))
        action = self.env["ir.actions.actions"]._for_xml_id("itq_event_management.itq_event_request_review_action")
        if self.state == 'under_approve':
            action = self.env["ir.actions.actions"]._for_xml_id(
                "itq_event_management.itq_event_request_approve_action")
        self.state = 'rejected'
        self.send_notification_to_creator()
        action['target'] = 'main'
        return action

    def check_team_member_count(self):
        for record in self:
            if self.organizer_team == 'public_relation_department' and not record.team_member_ids:
                raise ValidationError(_("The organizer team must have at least one record"))

    def to_confirm(self):
        self.ensure_one()
        if not self.organizer_team:
            raise ValidationError(_("Organizer Team is required"))

        self.check_team_member_count()
        if self.state != 'under_approve':
            raise ValidationError(_("State must be Under Approve"))
        self.state = 'confirmed'
        self.send_notification_to_creator()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "itq_event_management.itq_event_request_approve_action")
        action['target'] = 'main'
        return action

    @api.constrains('event_number_of_days')
    def check_event_number_of_days(self):
        for record in self:
            if record.event_number_of_days <= 0:
                raise ValidationError(_('Event Number of Days must be greater than 0'))

    @api.constrains('expected_number_of_guests')
    def check_expected_number_of_guests(self):
        for record in self:
            if record.expected_number_of_guests <= 0:
                raise ValidationError(_('Expected Number of Guests must be greater than 0'))

    @api.constrains('internal_guest_count', 'expected_number_of_guests')
    def check_internal_guest_count(self):
        for record in self:
            if record.internal_guest_count < 0:
                raise ValidationError(_('Internal Guest Count must be greater than or equal 0'))
            if record.internal_guest_count > record.expected_number_of_guests:
                raise ValidationError(_('Internal Guest Count must be less than or equal Expected Number of Guests'))

    @api.constrains('external_guest_count', 'expected_number_of_guests')
    def check_external_guest_count(self):
        for record in self:
            if record.external_guest_count < 0:
                raise ValidationError(_('External Guest Count must be greater than or equal 0'))
            if record.external_guest_count > record.expected_number_of_guests:
                raise ValidationError(_('External Guest Count must be less than or equal Expected Number of Guests'))

    @api.constrains('contact_number')
    def check_contact_number(self):
        for record in self:
            if record.contact_number and not self._validate_phone_number(record.contact_number):
                raise ValidationError(_("Invalid contact number format"))

    @api.constrains('guest_responsible_mobile')
    def check_guest_responsible_mobile(self):
        for record in self:
            if record.guest_responsible_mobile and not self._validate_phone_number(record.guest_responsible_mobile):
                raise ValidationError(_("Invalid Guest responsible mobile format"))

    @api.constrains('organizer_phone')
    def check_organizer_phone(self):
        for record in self:
            if record.organizer_phone and not self._validate_phone_number(record.organizer_phone):
                raise ValidationError(_("Invalid organizer phone format"))

    @api.constrains('organizer_mobile')
    def check_organizer_phone(self):
        for record in self:
            if record.organizer_mobile and not self._validate_phone_number(record.organizer_mobile):
                raise ValidationError(_("Invalid organizer mobile format"))

    @api.constrains('guest_responsible_phone')
    def check_guest_responsible_phone(self):
        for record in self:
            if record.guest_responsible_phone and not self._validate_phone_number(record.guest_responsible_phone):
                raise ValidationError(_("Invalid Guest responsible phone format"))

    @api.constrains('contact_email')
    def check_contact_email(self):
        for record in self:
            if record.contact_email and not self._validate_email(record.contact_email):
                raise ValidationError(_("Invalid Contact email format"))

    @api.constrains('organizer_email')
    def check_organizer_email(self):
        for record in self:
            if record.organizer_email and not self._validate_email(record.organizer_email):
                raise ValidationError(_("Invalid organizer email format"))

    def add_mandatory_amenities(self):
        amenities = self.env['itq.amenity.specification'].search(
            [('is_mandatory', '=', True), ('state', '=', 'active')])
        default_value = []
        for amenity in amenities:
            default_value.append((0, 0, {'amenity_specification_id': amenity.id}))
        return default_value

    def add_mandatory_catering(self):
        caterings = self.env['itq.catering.type'].search([('is_mandatory', '=', True), ('state', '=', 'active')])
        default_value = []
        for catering in caterings:
            default_value.append((0, 0, {'catering_type_id': catering.id}))
        return default_value

    def send_notification_to_department_manager_id(self):
        if self.department_id.manager_id.work_email:
            mail_template = self.env.ref('itq_event_management.itq_notify_department_manager_email_template')
            email_to = self.department_id.manager_id.work_email
            mail_template.send_mail(self.id, email_values={'email_to': email_to}, force_send=True)

    def send_notification_to_creator(self):
        mail_template = self.env.ref('itq_event_management.itq_notify_creator_email_template')
        email_to = self.create_uid.create_employee_id.work_email
        mail_template.send_mail(self.id, email_values={'email_to': email_to}, force_send=True)

    @api.constrains('event_program_line_ids', 'event_program_attachment_ids')
    def constraint_event_program_line_ids(self):
        for rec in self:
            if not rec.event_program_attachment_ids and not rec.event_program_line_ids:
                raise ValidationError(
                    _('You must fill at least one of Event Program Attachment or Event Program Lines'))

    @api.constrains('event_number_of_days')
    def constraint_event_number_of_days(self):
        for record in self:
            if record.event_number_of_days > 100:
                raise ValidationError(_('Event Number of Days must be less than or equal 100'))

    @api.onchange('event_number_of_days')
    def onchange_event_number_of_days(self):
        self.event_program_line_ids = False

    @api.depends('name', 'event_attraction_id')
    def _compute_calendar_name(self):
        for record in self:
            record.calendar_name = record.name + ' | ' + record.event_attraction_id.name

    @api.constrains('rehearsal_date', 'event_date')
    def constraint_rehearsal_date(self):
        for record in self:
            if record.rehearsal_date and record.rehearsal_date >= record.event_date:
                raise ValidationError(_('Rehearsal Date must be less than Event Date'))

    @api.depends('event_date', 'event_number_of_days')
    def _compute_event_date_end(self):
        for record in self:
            event_date_end = record.event_date + timedelta(days=record.event_number_of_days - 1)
            record.event_date_end = event_date_end
            if event_date_end < datetime.now():
                record.is_ended_event = True
            else:
                record.is_ended_event = False

    @api.constrains('event_date', 'event_type_id')
    def constraint_event_date(self):
        for record in self:
            utc_date = pytz.timezone("UTC").localize(
                fields.Datetime.from_string(record.event_date)).astimezone(
                pytz.timezone(self.env.user.tz or "Asia/Riyadh")).replace(tzinfo=None).date()
            min_number_of_days = fields.Date.today() + timedelta(
                record.event_type_id.minimum_days_before_request)
            if utc_date <= min_number_of_days:
                raise ValidationError(
                    _('Event start date must be greater than {}').format(min_number_of_days))

    @api.depends('amenity_specification_line_ids', 'amenity_specification_line_ids.amenity_specification_id')
    def compute_used_amenity_specification_ids(self):
        for record in self:
            record.used_amenity_specification_ids = record.amenity_specification_line_ids.amenity_specification_id

    @api.depends('catering_type_line_ids', 'catering_type_line_ids.catering_type_id')
    def compute_used_catering_type_ids(self):
        for record in self:
            record.used_catering_type_ids = record.catering_type_line_ids.catering_type_id

    @api.model
    def get_readonly_exclude_fields(self):
        return ['organizer_team', 'organizer_email', 'organizer_phone', 'organizer_mobile', 'organizer_name',
                'team_member_ids', 'invitee_ids']

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id, view_type, **options)
        if view_type == 'form':
            doc = etree.XML(result['arch'])
            x2m_fields = [item[0] for item in
                          filter(lambda i: i[1].type in ['one2many', 'many2many'], self._fields.items())]
            sub_x2m_fields = []
            for x2m_field in x2m_fields:
                sub_x2m_fields += doc.xpath("//field[@name='{}']//field".format(x2m_field))
            for field in doc.xpath("//field"):
                if field not in sub_x2m_fields and field.get('name') not in self.get_readonly_exclude_fields():
                    modifiers = field.get("modifiers") and json.loads(field.get("modifiers")) or {}
                    if modifiers.get('readonly'):
                        if modifiers['readonly'] is not True and isinstance(modifiers.get('readonly'), (list, tuple)):
                            modifiers['readonly'] = ['|', ('state', '!=', 'draft')] + modifiers['readonly']
                    else:
                        modifiers['readonly'] = [('state', '!=', 'draft')]
                    field.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_("You can delete record in draft state only."))
        return super(EventRequest, self).unlink()

    @api.onchange('organizer_team')
    def onchange_organizer_team(self):
        if self.organizer_team == 'public_relation_department':
            self.organizer_name = None
            self.organizer_phone = None
            self.organizer_mobile = None
            self.organizer_email = None
        else:
            self.team_member_ids = None

    @api.onchange('event_attraction_id')
    def onchange_event_attraction_id(self):
        self.other_event_attraction = False

    def show_event_permissions(self):
        self.ensure_one()
        return {
            'name': _('Event Permissions'),
            'view_mode': 'tree,form',
            'res_model': 'itq.event.permission',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('event_request_id', '=', self.id)],
            'context': {
                'create': False
            }
        }

    def add_event_permission(self):
        self.ensure_one()
        return {
            'name': _('Event Permissions'),
            'view_mode': 'form',
            'res_model': 'itq.event.permission',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('event_request_id', '=', self.id)],
            'context': {
                'default_event_request_id': self.id
            }
        }
