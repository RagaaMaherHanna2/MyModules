from odoo import api, fields, models
from calendar import monthrange


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def write(self, vals):
        res = super(HrContract, self).write(vals)
        if self.env['ir.config_parameter'].sudo().get_param(
                'itq_auto_generate_employee_list.is_auto_generated_list'):
            if 'state' in vals.keys():
                for rec in self:
                    rec.employee_id.reflect_on_employee_list()

        return res

