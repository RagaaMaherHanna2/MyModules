from odoo import api, fields, models, _
from datetime import datetime, date
import calendar


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_contract_basic_allowance_value(self, contract, allowances=[], calc_based_on='basic', accrual_rule_id=None,
                                           allowances_calc='exclude'):
        if contract.is_project_variable_wage and contract.project_variable_ids:
            projects_salary = self.get_employee_projects_variable_salary(contract)
            if calc_based_on == 'basic':
                cost = projects_salary
            else:
                if allowances_calc == 'exclude':
                    benefit_obj = contract.valuable_benefit_ids.filtered(
                        lambda b: b.benefit_id.id not in allowances)
                else:
                    benefit_obj = contract.valuable_benefit_ids.filtered(
                        lambda b: b.benefit_id.id in allowances)
                percent_benefit = benefit_obj.filtered(lambda b: b.calculation_type == 'perc_from_bs')
                amount_benefit = benefit_obj - percent_benefit
                benefit_values = sum(amount_benefit.mapped("calculated_value"))
                benefit_values += sum([(line.benefit_value / 100) * projects_salary for line in percent_benefit])
                cost = projects_salary + benefit_values
        else:
            cost = super(HrPayslip, self).get_contract_basic_allowance_value(contract, allowances=allowances,
                                                                             calc_based_on=calc_based_on,
                                                                             accrual_rule_id=accrual_rule_id,
                                                                             allowances_calc=allowances_calc)
        return cost

    def get_employee_projects_variable_salary(self, contract):
        employee_projects = contract.employee_id.analytic_line_ids.filtered(
            lambda l: not l.end_date or (
                    l.start_date.month >= self.date_from.month and l.end_date.month <= self.date_to.month))
        total_projects_salary = 0.0
        if employee_projects:
            for line in employee_projects:
                end_date = self.date_to
                if line.end_date:
                    end_date = line.end_date
                intersection_days = self.get_intersection_days(start_date=line.start_date, end_date=end_date)
                project = self.env['project.project'].search(
                    [('analytic_account_id', '=', line.analytic_account_id.id)], limit=1)

                project_variable_line = contract.project_variable_ids.filtered(
                    lambda pv: pv.project_id == project)
                if project_variable_line:
                    employee_salary = project_variable_line.project_variable
                    if not project_variable_line.has_payslips:
                        project_variable_line.has_payslips = True
                else:
                    employee_salary = contract.wage

                variable_per_day = employee_salary / calendar.monthrange(self.date_from.year, self.date_from.month)[1]
                total_projects_salary += (variable_per_day * intersection_days)

        return total_projects_salary

    def get_benefit_calculated_value(self, contract=False, salary_rule=False):
        calculated_value = super(HrPayslip, self).get_benefit_calculated_value(contract, salary_rule)
        valuable_benefit_ids = contract.valuable_benefit_ids.filtered(
            lambda l: l.benefit_id == salary_rule.benefit_id and l.benefit_id.calculation_type == 'perc_from_bs')
        if contract.is_project_variable_wage and contract.project_variable_ids and valuable_benefit_ids:
            # get employee allocated projects in this payslip period
            total_projects_benefit_value = self.get_employee_projects_variable_salary(contract)
            calculated_value = sum(
                [(benefit.benefit_value / 100) * total_projects_benefit_value for benefit in valuable_benefit_ids])
        return calculated_value

    def get_contract_benefit(self, contract=False, salary_rule=False):
        valuable_benefit_ids = contract.valuable_benefit_ids.filtered(
            lambda l: l.benefit_id == salary_rule.benefit_id and l.benefit_id.calculation_type == 'perc_from_bs')
        if contract.is_project_variable_wage and contract.project_variable_ids and valuable_benefit_ids:
            benefit_value = self.get_benefit_calculated_value(contract, salary_rule)
        else:
            benefit_value = super(HrPayslip, self).get_contract_benefit(contract, salary_rule)

        return benefit_value

    def get_contract_basic(self, contract=False):
        if contract and contract.is_project_variable_wage and contract.project_variable_ids:
            return self.get_employee_projects_variable_salary(contract) or -1
        else:
            return super(HrPayslip, self).get_contract_basic(contract=contract)
