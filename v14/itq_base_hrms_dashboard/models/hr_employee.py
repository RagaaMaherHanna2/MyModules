from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    hiring_date = fields.Date(related='first_contract_date', store=True)
    employee_age = fields.Integer(related='age', store=True)