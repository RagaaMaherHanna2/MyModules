from odoo import fields, models, tools, api


class HrEmployeeData(models.Model):
    _inherit = "hr.employee.data"

    project_id = fields.Many2one(comodel_name="project.project")

    def _select(self):
        return super()._select() + ", EMP.project_id as project_id"


    def _group_by(self):
        return super()._group_by() + ", EMP.project_id"
