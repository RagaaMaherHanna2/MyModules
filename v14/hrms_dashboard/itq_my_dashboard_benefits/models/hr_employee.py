from odoo import models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def get_user_employee_details(self):
        employee = super().get_user_employee_details()
        non_valuable_benefit_ids = valuable_benefit_ids = []
        non_valuable_benefit_ids_count = valuable_benefit_ids_count = benefit_change_request_count = non_periodical_benefit_request_count = 0
        if employee:
            benefit_change_request_ids = self.env['itq.contract.benefit.change.request'].sudo().search(
                [('employee_id', '=', employee[0]['id'])]).ids
            non_periodical_benefit_request_ids = self.env['itq.non.periodical.benefit.request'].sudo().search(
                [('employee_id', '=', employee[0]['id'])]).ids
            if benefit_change_request_ids:
                benefit_change_request_count = len(benefit_change_request_ids)
            if non_periodical_benefit_request_ids:
                non_periodical_benefit_request_count = len(non_periodical_benefit_request_ids)
            if employee[0]['contract_id']:
                employee_contract = self.env['hr.contract'].sudo().browse(employee[0]['contract_id'][0])
                if employee_contract.non_valuable_benefit_ids:
                    non_valuable_benefit_ids = employee_contract.non_valuable_benefit_ids.ids
                    non_valuable_benefit_ids_count = len(non_valuable_benefit_ids)

                if employee_contract.valuable_benefit_ids:
                    valuable_benefit_ids = employee_contract.valuable_benefit_ids.ids
                    valuable_benefit_ids_count = len(valuable_benefit_ids)

            data = {
                'non_valuable_benefit_ids': non_valuable_benefit_ids,
                'non_valuable_benefit_ids_count': non_valuable_benefit_ids_count,
                'valuable_benefit_ids': valuable_benefit_ids,
                'valuable_benefit_ids_count': valuable_benefit_ids_count,
                'benefit_change_request_ids': benefit_change_request_ids,
                'benefit_change_request_count': benefit_change_request_count,
                'non_periodical_benefit_request_ids': non_periodical_benefit_request_ids,
                'non_periodical_benefit_request_count': non_periodical_benefit_request_count,
            }
            employee[0].update(data)
            return employee
        else:
            return False
