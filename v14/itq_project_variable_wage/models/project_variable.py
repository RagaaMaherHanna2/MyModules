from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectVariable(models.Model):
    _name = 'project.variable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_id'

    contract_id = fields.Many2one('hr.contract', string="Contract")
    project_id = fields.Many2one('project.project', string="Project", required=True)
    project_variable = fields.Float(string="Variable Salary", tracking=True)
    has_payslips = fields.Boolean()

    @api.constrains('project_variable')
    def variable_project_variable(self):
        for rec in self:
            if rec.project_variable <= 0.0:
                raise ValidationError(_("Variable Salary Must Be Grater Than 0.0"))

    def unlink(self):
        if self.has_payslips:
            raise ValidationError(_('Can not delete project variable lines that have because paid payslips.'))
        return super(ProjectVariable, self).unlink()
