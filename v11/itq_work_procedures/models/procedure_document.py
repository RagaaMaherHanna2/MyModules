# -*- coding: utf-8 -*-
import mimetypes

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProcedureDocument(models.Model):
    _name = 'procedure.document'
    _description = "Procedure Document"

    _sql_constraints = [
        ("unique_name_procedure_id", "UNIQUE (name,procedure_id)",
         _("Documents names must be unique for the same procedure.")),
        ("unique_name_approval_id", "UNIQUE (name,approval_id)", _("لايمكن تكرر اسماء النماذج.")),
    ]

    procedure_docs_sequence = fields.Char(string="Sequence", compute='_compute_procedure_docs_sequence')
    approval_docs_sequence = fields.Char(string="Sequence", compute='_compute_approval_docs_sequence')

    name = fields.Char(string='Document Name', required=True)
    aim = fields.Selection([('procedure', 'Procedure'),
                            ('step', 'Step')], string='Document Aim', required=True)
    description = fields.Text(string="Description")
    procedure_id = fields.Many2one('work.procedure')
    step_id = fields.Many2one('procedure.step', string='Related Step')
    approval_id = fields.Many2one('approval.tracking.line', string='Related Approval')
    document_file = fields.Binary(string='Document File', required=True, attachment=True)
    file_name = fields.Char(string='Decision File')
    active_document = fields.Boolean(default=True)

    @api.constrains('document_file')
    def _document_file_constrains(self):
        for rec in self:
            if not rec.document_file:
                raise ValidationError('لابد من ادخال مرفق النموذج')

    @api.constrains('file_name')
    def _file_name_constrains(self):
        for rec in self:
            mimetype = None
            if mimetype is None and rec.file_name:
                mimetype = mimetypes.guess_type(rec.file_name)[0]
                if not mimetype in ['application/pdf', 'application/msword', 'application/excel',
                                    'application/vnd.ms-excel', 'image/png', 'image/jpg',
                                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    raise ValidationError('يمكنك اضافة صيغة docx/pdf فقط')

    @api.onchange('aim')
    def _onchange_aim(self):
        if self.aim:
            self.step_id = False

    @api.depends('procedure_id.procedure_doc_ids')
    def _compute_procedure_docs_sequence(self):
        for line in self:
            no = 0
            for l in line.procedure_id.procedure_doc_ids:
                no += 1
                l.procedure_docs_sequence = no

    @api.depends('approval_id.approval_doc_ids')
    def _compute_approval_docs_sequence(self):
        for line in self:
            no = 0
            for l in line.approval_id.approval_doc_ids:
                no += 1
                l.approval_docs_sequence = no
