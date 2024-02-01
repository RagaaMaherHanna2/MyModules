from datetime import datetime, timedelta
import re
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError
from phonenumbers import parse, is_valid_number, NumberParseException
from datetime import timedelta
from lxml import etree
import json


class VisitRequest(models.Model):
    _name = "itq.visit.request"
    _inherit = 'mail.thread'
    _description = _('Visit Request')

    name = fields.Char(string='Request Number', readonly=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('under_review', 'Under Review'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected')],
                             default='draft', readonly=True, tracking=True)
    request_date = fields.Datetime(default=lambda self: datetime.now(), readonly=True, tracking=True)

    request_type = fields.Selection([
        ('visit', 'Visit Request'),
        ('photoshoot', 'Photoshoot Request')], string='Request Type', required=True)

    request_source = fields.Selection([
        ('internal', 'Internal (Backend)'),
        ('external', 'External (Website)')], string='Visit Source', readonly=True)

    visit_type = fields.Selection([
        ('visit', 'Visit'),
        ('meeting', 'meeting')], string='Visit Type', required=True)
    visit_classification_id = fields.Many2one('itq.visit.classification', ondelete='restrict',
                                              domain=[('state', '=', 'active')])

    visitor_type = fields.Selection([
        ('individual', 'Individual'),
        ('organization', 'Organization')], string='Visitor Type', required=True)

    #  Visit Requester Info
    requester_name = fields.Char(string="Requester Name", required=True)
    phone_number = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email', required=True)
    visit_reason = fields.Text(string='Visit Reason')

    # Organization Visitor Info
    organization_id = fields.Many2one('itq.organization.type', ondelete='cascade', domain=[('state', '=', 'active')])

    # Visit request type Data
    to_visit_attraction_ids = fields.Many2many('itq.attraction.location', compute='_compute_to_visit_attraction_ids')
    to_visit_attraction_id = fields.Many2one('itq.attraction.location', string='To Visit Attraction',
                                             ondelete='restrict')

    # meeting request type Info
    to_visit_department_id = fields.Many2one('hr.department', ondelete='cascade', domain=[('is_visitable', '=', True)])
    is_research_department = fields.Boolean(related='to_visit_department_id.is_research_department')
    # research department Info
    research_type_id = fields.Many2one('itq.research.type', ondelete='cascade', domain=[('state', '=', 'active')])
    research_topic = fields.Text(string='Research Topic')

    # Photoshoot request type Info
    photoshoot_type = fields.Selection([
        ('record', 'Record'),
        ('live', 'Live'),
        ('other', 'Other')], string='Visitor Type')
    other_photoshoot_type = fields.Char(string='Other Photoshoot Type')

    current_resource_calendar_id = fields.Many2one('resource.calendar', compute='_compute_current_resource_calendar')
    visit_date_from = fields.Datetime(string='From', required=True)
    visit_date_to = fields.Datetime(string='To', required=True)

    expected_number = fields.Integer(string='Expected Number', required=True)
    # visit_letter_id = fields.Many2one('ir.attachment',  string='Visit Letter')
    visit_letter_id = fields.Binary(string='Visit Letter')
    file_name = fields.Char(store=True)

    document_visit = fields.Boolean(string='Document Visit?')

    documentation_type_id = fields.Many2one('itq.documentation.type', string='Documentation Type',
                                            domain=[('state', '=', 'active')])

    visitor_ids = fields.One2many('itq.visitor', 'visit_request_id', 'Visitors')
    extra_notes = fields.Text(string='Extra Notes')

    # TODO Onchange selections

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'visit.request.sequence')], limit=1)
        vals['name'] = sequence.next_by_id()
        return super(VisitRequest, self).create(vals)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form' and self.state != 'draft':
            for node in arch.xpath("//field[not(@readonly)]"):
                node.set('readonly', 'True')
        return arch, view

    @api.constrains('visit_date_from', 'visit_date_to')
    def validate_visit_dates(self):
        for rec in self:
            if rec.visit_date_from and rec.visit_date_to and rec.visit_date_to < rec.visit_date_from:
                raise ValidationError(_('Valid End Date Must be Less than Valid Start Date'))

    @api.constrains('phone_number')
    def validate_phone_number(self):
        for rec in self:
            if rec.phone_number and not rec._validate_phone_number(rec.phone_number):
                raise ValidationError(_('Not Valid Phone Number!'))

    @api.constrains('email')
    def validate_email(self):
        for rec in self:
            if rec.email and not rec._validate_email(rec.email):
                raise ValidationError(_('Not Valid Email!'))

    @api.constrains('visitor_ids')
    def validate_visitor_phone_email(self):
        for rec in self:
            if rec.visitor_ids:
                for visitor in rec.visitor_ids:
                    if not rec._validate_email(visitor.email):
                        raise ValidationError(_('Not Valid Visitor {} Email!').format(_(visitor.name)))
                    if not rec._validate_phone_number(visitor.mobile):
                        raise ValidationError(_('Not Valid Visitor {} Mobile!').format(_(visitor.name)))

    @api.depends('request_type')
    def _compute_to_visit_attraction_ids(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.request_type:
                domain = [('state', '=', 'active')]
                if rec.request_type == 'visit':
                    domain.append(('is_visit', '=', True))
                elif rec.request_type == 'photoshoot':
                    domain.append(('is_photo_shoot', '=', True))
            rec.to_visit_attraction_ids = self.env['itq.attraction.location'].search(domain)

    @api.depends('to_visit_attraction_id', 'to_visit_department_id')
    def _compute_current_resource_calendar(self):
        for rec in self:
            current_resource_calendar = False
            if rec.to_visit_attraction_id:
                current_resource_calendar = rec.to_visit_attraction_id.resource_calendar_id
            elif rec.to_visit_department_id:
                current_resource_calendar = rec.to_visit_department_id.resource_calendar_id
            rec.current_resource_calendar_id = current_resource_calendar

    def submit_to_review(self):
        for rec in self:
            rec.state = 'under_review'
            rec.send_notification(email_to=rec.email,
                                  msg=_('Your request has been successfully created with number {} .'.format(rec.name)))

    def action_return(self):
        for rec in self:
            rec.state = 'draft'
            # rec.send_notification(email_to=rec.email)

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.send_notification(email_to=rec.email,
                                  msg=_(
                                      'For sorry your request with number {} has been rejected call us for more info.'.format(
                                          rec.name)))

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            rec.send_notification(email_to=rec.email,
                                  msg=_(
                                      'Your request with number {} has been Confirmed waiting to see you.'.format(
                                          rec.name)))

    @api.model
    def _validate_phone_number(self, phone_number):
        try:
            number = parse(phone_number)
            if not is_valid_number(number):
                return False
            return True
        except NumberParseException:
            return False

    @api.model
    def _validate_email(self, email):
        regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        return bool(re.match(regex, email))

    def send_email(self, email_to='', msg=''):
        mail_template = self.env.ref('itq_event_management.visit_request_mail_notify')
        body_html = """
                    <div style="margin: 0px; padding: 0px;">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%"
                               style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                            <tr>
                                <td valign="top" style="font-size: 13px;">
                                    <div>
                                        Hi {},
                                        <br/>
                                        <br/>
                                        {}
                                        <br/>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </div>        
                """.format(self.requester_name, msg)
        mail_template.send_mail(self.id, email_values={'email_to': email_to, 'body_html': body_html}, force_send=True)

    def send_sms(self, phone_to='', msg=''):
        # TODO waiting
        return True

    def send_notification(self, email_to='', phone_to='', msg=''):
        self.send_email(email_to=email_to, msg=msg)
        self.send_sms(phone_to=phone_to, msg=msg)
