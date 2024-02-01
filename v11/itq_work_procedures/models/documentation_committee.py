# -*- coding: utf-8 -*-
import mimetypes

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DocumentationCommittee(models.Model):
    _name = 'documentation.committee'
    _description = "Documentation Committee"

    _sql_constraints = [
        ("unique_name", "UNIQUE (name)", _("This Committee Name has been registered before."))]

    name = fields.Char(string="Committee Name", required=True, track_visibility='onchange')
    committee_creation_date = fields.Date(string='Creation Date', required=True)
    decision_no = fields.Char(string="Decision No")
    decision_date = fields.Date(string='Decision Date')
    decision_file = fields.Binary(string='Decision File', required=True, attachment=True)
    file_name = fields.Char(string='Decision File')
    member_ids = fields.One2many('committee.member', 'committee_id', string='Members')
    active_committee = fields.Boolean(default=False, string='Active')

    @api.constrains('active_committee')
    def check_active_constrains(self):
        for rec in self:
            if rec.active_committee and self.search([('active_committee', '=', True), ('id', '!=', rec.id), ]):
                raise ValidationError(_('you have to choose just one active Committee'))

    @api.constrains('file_name')
    def _file_name_constrains(self):
        for rec in self:
            mimetype = None
            if mimetype is None and rec.file_name:
                mimetype = mimetypes.guess_type(rec.file_name)[0]
                if not mimetype in ['application/pdf', 'application/msword',
                                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    raise ValidationError('يمكنك اضافة صيغة docx/pdf فقط')
