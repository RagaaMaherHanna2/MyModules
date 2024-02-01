from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    related_accountant_user_ids = fields.Many2many('res.users',
                                                   string='Related Accountant User')

    def _compute_user_related_collect_custody_ids(self):
        users = self.env['res.users'].search([])
        for user in users:
            related_collection_custody = False
            related_employees_partners = self.search(
                [('related_accountant_user_ids', 'in', user.id)]).mapped('user_partner_id')
            if related_employees_partners:
                related_collection_custody = self.env['itq.collect.custody.request'].search(
                    [('payment_id.collected_by_employee_id', 'in', related_employees_partners.ids)])
            user.related_collect_custody_ids = related_collection_custody

    def write(self, values):
        res = super(HrEmployee, self).write(values)
        if 'related_accountant_user_ids' in values.keys() and values.get('related_accountant_user_ids', False):
            self._compute_user_related_collect_custody_ids()
        return res
