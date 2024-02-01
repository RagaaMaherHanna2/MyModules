# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProcedureResource(models.Model):
    _name = 'procedure.resource'
    _description = "Procedure Resource"

    _sql_constraints = [
        ("unique_name", "UNIQUE (name,procedure_id)",
         _("Resources names must be unique per procedure."))
    ]

    sequence = fields.Char(string="Sequence", compute='_sequence_ref')
    name = fields.Char(string='Resource Name', required=True)
    aim = fields.Selection([('procedure', 'Procedure'),
                            ('step', 'Step')], string='Resource Aim', required=True)
    procedure_id = fields.Many2one('work.procedure')
    step_id = fields.Many2one('procedure.step', string='Related Step')
    resource_type = fields.Selection([('hr', 'الموارد البشرية'), ('info', 'المعلومات'),
                                      ('contacts', 'وسائل الاتصال'), ('offices', 'المكاتب '),
                                      ('assets', 'الأصول '), ('other', 'اخري '), ],
                                     default='hr', string='Type', required=True)
    description = fields.Text(string="Description")
    employee_categ = fields.Selection([('2', 'ضباط'), ('1', 'افراد'), ('3', 'مدنيين')],
                                      string='التصنيف العام للموارد البشرية')
    job_id = fields.Many2one('itq.jobs', string='Job Name', domain="[('itq_system_categ', '=', employee_categ)]")
    jobs_access_ids = fields.Many2many('job.access', string='Job Access Name')
    job_code = fields.Char('Job Code', readonly=True)

    asset_id = fields.Many2one('itq.fixed.asset', string='Asset')
    resource_description = fields.Text(string="Resource Description", required=True)
    resource_name = fields.Char('Resource')

    @api.model
    def create(self, vals):
        res = super(ProcedureResource, self).create(vals)
        if res.resource_type == 'hr':
            if res.procedure_id.code:
                res.job_code = res.procedure_id.code + '/' + self.env['ir.sequence'].next_by_code('job.code.seq')
        return res

    def get_steps_domain(self):
        procedure_steps = False
        if self.procedure_id.procedure_step_ids:
            procedure_steps = self.procedure_id.procedure_step_ids.ids
        return [('id', 'in', procedure_steps)]

    @api.depends('procedure_id.procedure_resource_ids')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.procedure_id.procedure_resource_ids:
                no += 1
                l.sequence = no

    @api.onchange('aim')
    def _onchange_aim(self):
        for line in self:
            if line.aim:
                line.step_id = False
