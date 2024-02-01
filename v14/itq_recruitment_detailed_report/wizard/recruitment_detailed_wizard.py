from datetime import date, timedelta
import io
import json
import calendar
from dateutil.relativedelta import relativedelta

from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell


def _get_months(months_range=range(1, 13)):
    """
    returns list of tuples of str(month_num, month_name)
    """
    return [(str(month), str(calendar.month_name[month])) for month in months_range]


DATA_HEADER_LIST = {'hired_count': 'Hired',
                    'assignation_count': 'Assignation',
                    'availability_count': 'Availability',
                    'planned_count': 'Planned',
                    'allocated_count': 'Allocated',
                    'actually_resigned_count': 'Actually resigned',
                    'planned_resigned_count': 'Planned Resigned',
                    'expiring_count': 'Expiring Contracts'}


def _get_years():
    """
    returns list of tuples of str(year_num, year_num)
    """
    current_year = fields.date.today().year
    return [(str(year), str(year)) for year in range(current_year - 10, current_year + 10)]


class RecruitmentDetailed(models.TransientModel):
    _name = "recruitment.detailed.wizard"
    _description = "Recruitment Detailed Wizard"

    report_option = fields.Selection([('this_year', 'This Year'),
                                      ('previous_year', 'Previous Year'),
                                      ('custom_range', 'Custom Range')], string='Select Period', default='this_year',
                                     required=True)
    from_month = fields.Selection(_get_months())
    from_year = fields.Selection(_get_years())
    to_month = fields.Selection(_get_months())
    to_year = fields.Selection(_get_years())

    @api.onchange('report_option')
    def _onchange_report_option(self):
        if self.report_option:
            self.from_month = self.from_year = self.to_month = self.to_year = False

    def _test_dates_validation(self):

        if int(self.from_year) == int(self.to_year) and int(self.from_month) > int(self.to_month):
            raise ValidationError(_('Target Month Must be grater than lunching Month of the same year'))

        if int(self.from_year) > int(self.to_year):
            raise ValidationError(_('Target Year Must be grater than lunching year'))

    @staticmethod
    def get_period_range(form_data):
        """ 
        This function calculate period range of the report
            form_data : dict of wizard keys and values
            returns list of dict contains year and it's months range
        """
        period_range = []
        report_option = form_data['report_option']
        if report_option == 'custom_range':
            from_year = int(form_data['from_year'])
            from_month = int(form_data['from_month'])
            to_year = int(form_data['to_year'])
            to_month = int(form_data['to_month'])
            if from_year == to_year:
                period_range.append({'year': from_year, 'months_range': range(from_month, to_month + 1)})
            else:
                for year in range(from_year, to_year + 1):
                    if year == from_year:
                        months_range = range(from_month, 13)
                    elif year == to_year:
                        months_range = range(1, to_month)
                    else:
                        months_range = range(1, 13)

                    period_range.append({'year': year,
                                         'months_range': months_range})
        else:
            year = date.today().year
            if report_option == 'previous_year':
                year = date.today().year - 1
            period_range.append({'year': year, 'months_range': range(1, 13)})
        print(period_range)
        return period_range

    @staticmethod
    def set_format(workbook):
        format0 = workbook.add_format({'font_size': 15, 'bg_color': '#D3D3D3', 'border': True})
        format0.set_align('center')
        format1 = workbook.add_format({'font_size': 12, 'bg_color': '#D3D3D3', 'border': True})
        format1.set_align('center')
        format2 = workbook.add_format({'font_size': 12})
        format2.set_align('center')
        format3 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF', 'border': True})
        format3.set_align('center')
        format4 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF', 'border': True, 'num_format': '0.0%'})
        format4.set_align('center')
        return [format0, format1, format2, format3, format4]

    @staticmethod
    def _get_department_jobs_details(department, report_data, month_start, month_end):
        department_jobs = report_data['matched_jobs']
        year = month_start.year
        month = month_start.month
        department_jobs_details = []
        """
        department_jobs_details list design
            department_jobs_details = [
                {
                    'job_name',
                    'department_job_month_details':
                        {
                            'data': val
                            'data': val
                            'data': val
                        }
                    ]
                }
            ]
        """
        for job in department_jobs:
            running_contracts = report_data['hired_contracts'].filtered(
                lambda c: c.job_id == job and c.department_id == department)

            hired_count = len(running_contracts.filtered(
                lambda c: month_start <= c.first_contract_date <= month_end))

            job_applications = report_data['job_applications'].filtered(
                lambda a: a.job_id == job and a.department_id == department)

            assignation_count = len(
                job_applications.filtered(
                    lambda a: a.create_date.year == year and a.create_date.month == month))

            availability_count = len(
                job_applications.filtered(
                    lambda a: a.availability and a.availability.year == year and a.availability.month == month))

            planned_count = sum(report_data['hiring_plans'].filtered(
                lambda
                    p: p.plan_line_id.department_id == department and p.plan_line_id.job_id == job and month_start <= p.month_date <= month_end).mapped(
                'planned_count'))

            allocated_count = len(report_data['allocated_contracts'].filtered(
                lambda
                    c: c.job_id == job and c.department_id == department and month_start > c.first_contract_date and month_end <= c.date_end))

            termination_requests = report_data['termination_requests'].filtered(
                lambda
                    r: r.contract_id.job_id == job and r.department_id == department and month_start <= r.effective_date <= month_end)
            actually_resigned_count = len(termination_requests.filtered(lambda r: r.state == 'terminated'))

            planned_resigned_count = len(
                termination_requests.filtered(lambda r: r.state not in ['cancel', 'terminated']))

            expiring_count = len(report_data['expiring_contracts'].filtered(
                lambda
                    c: c.job_id == job and c.department_id == department and c.date_end and month_start <= c.date_end <= month_end))

            department_jobs_details.append({'job_name': job.name,
                                            'department_job_month_details': {'hired_count': hired_count,
                                                                             'assignation_count': assignation_count,
                                                                             'availability_count': availability_count,
                                                                             'planned_count': planned_count,
                                                                             'allocated_count': allocated_count,
                                                                             'actually_resigned_count': actually_resigned_count,
                                                                             'planned_resigned_count': planned_resigned_count,
                                                                             'expiring_count': expiring_count,
                                                                             }})
        return department_jobs_details

    def _prepare_report_data(self, p_start_date, p_end_date):
        """
            This function returns sum of departments and jobs that have data match report requirements
            within start and end period
        """
        # contracts that match hired employees in this period
        matched_departments = self.env['hr.department']
        matched_jobs = self.env['hr.job']
        try:
            open_contracts = self.env['hr.contract'].with_context(itq_ignore_apply_access=True).search(
                [('state', '=', 'open')])

            # all hired employees within this period
            hired_contracts = open_contracts.filtered(
                lambda c: c.job_id and p_start_date <= c.first_contract_date <= p_end_date)

            matched_departments |= hired_contracts.mapped('department_id')
            matched_jobs |= hired_contracts.mapped('job_id')

            # all contracts are going to expire within this period
            expiring_contracts = open_contracts.filtered(
                lambda c: c.job_id and c.date_end and p_start_date <= c.date_end <= p_end_date)

            matched_departments |= expiring_contracts.mapped('department_id')
            matched_jobs |= expiring_contracts.mapped('job_id')

            # job applications that have created and have availability date within this period
            job_applications = self.env['hr.applicant'].search(['|',
                                                                '&', ('create_date', '>=', p_start_date),
                                                                ('create_date', '<=', p_end_date),
                                                                '&', ('availability', '>=', p_start_date),
                                                                ('availability', '>=', p_end_date),
                                                                ]).filtered(lambda c: c.job_id)
            matched_departments |= job_applications.mapped('department_id')
            matched_jobs |= job_applications.mapped('job_id')

            # employees that planed to be hired within this period
            hiring_plans = self.env['itq.monthly.running.cost'].search(
                [('plan_line_id.state', 'in', ['reopen', 'confirm']),
                 ('month_date', '>=', p_start_date),
                 ('month_date', '<=', p_end_date),
                 ])
            matched_departments |= hiring_plans.mapped('plan_line_id').mapped('department_id')
            matched_jobs |= hiring_plans.mapped('plan_line_id').mapped('job_id')

            # allocated employees contracts were open but not hired within this period
            allocated_contracts = open_contracts.filtered(
                lambda c: c.job_id and c.date_end and p_start_date > c.first_contract_date and p_end_date <= c.date_end)

            matched_departments |= allocated_contracts.mapped('department_id')
            matched_jobs |= allocated_contracts.mapped('job_id')

            # termination requests that have effective date within this period
            termination_requests = self.env['itq.hr.termination.request'].search(
                [('effective_date', '>=', p_start_date),
                 ('effective_date', '<=', p_end_date)])
            matched_departments |= termination_requests.mapped('department_id')
            matched_jobs |= termination_requests.mapped('contract_id').filtered(lambda c: c.job_id).mapped('job_id')

            return {'matched_departments': matched_departments,
                    'matched_jobs': matched_jobs,
                    'hired_contracts': hired_contracts,
                    'expiring_contracts': expiring_contracts,
                    'job_applications': job_applications,
                    'hiring_plans': hiring_plans,
                    'allocated_contracts': allocated_contracts,
                    'termination_requests': termination_requests, }
        except Exception as e:
            print('_prepare_report_data', e)

    def sheet_writing(self, sheet, formats, p_range):
        months = _get_months(months_range=p_range['months_range'])
        first_month_num = int(months[0][0])
        last_month_num = int(months[-1][0])
        p_start_date = date.today().replace(year=int(p_range['year']), month=first_month_num, day=1)
        p_last_month = date.today().replace(year=int(p_range['year']), month=last_month_num, day=1)
        p_end_date = (p_last_month + relativedelta(months=1, day=1)) - timedelta(1)
        report_data = self._prepare_report_data(p_start_date, p_end_date)

        # list the header title of data which to be collected in dictionary to write the header of report
        # we should consider 2 columns of department and job
        merged_cols = 1 + (len(p_range['months_range']) * len(DATA_HEADER_LIST))
        sheet.set_column(0, 2, merged_cols)
        sheet.merge_range(0, 0, 1, merged_cols, 'Recruitment Detailed Report', formats[0])
        main_raw_start = 2
        main_col_start = 2

        main_raw_end = main_raw_start + 1
        col_end = merged_cols
        sheet.merge_range(main_raw_start, main_col_start, main_raw_end, col_end, p_range['year'],
                          formats[3])
        main_raw_start = main_raw_end + 1
        month_raw_start = main_raw_start
        month_col_start = 2
        matched_departments = report_data['matched_departments']
        if matched_departments:
            # Write months line
            try:
                for month in months:
                    month_number = int(month[0])
                    month_name = month[1]
                    month_col_end = month_col_start + len(DATA_HEADER_LIST) - 1
                    sheet.merge_range(month_raw_start, month_col_start, month_raw_start, month_col_end, month_name,
                                      formats[3])
                    # write header line
                    head_col_start = month_col_start
                    head_raw_start = month_raw_start + 1
                    for col in DATA_HEADER_LIST.keys():
                        sheet.write(head_raw_start, head_col_start, DATA_HEADER_LIST[col], formats[3])
                        head_col_start += 1

                    # Prepare this month department jobs data
                    month_start = date.today().replace(year=int(p_range['year']), month=month_number, day=1)
                    month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)

                    dep_raw_start = main_raw_start + 2
                    for department in matched_departments:
                        # let's get this department jobs details
                        department_jobs_details = self._get_department_jobs_details(department=department,
                                                                                    report_data=report_data,
                                                                                    month_start=month_start,
                                                                                    month_end=month_end)

                        if department_jobs_details:
                            # let's write department name
                            sheet.merge_range(dep_raw_start, 0, dep_raw_start, 1, department.name, formats[1])
                            job_line_raw_start = dep_raw_start + 1
                            # let's write department jobs details
                            for job_line in department_jobs_details:

                                sheet.write(job_line_raw_start, 1, job_line['job_name'], formats[3])
                                line_detail_col_start = month_col_start
                                for line_detail in job_line['department_job_month_details'].values():
                                    sheet.write(job_line_raw_start, line_detail_col_start, line_detail, formats[3])
                                    line_detail_col_start += 1
                                job_line_raw_start += 1

                            dep_raw_start = dep_raw_start + len(department_jobs_details) + 1

                    # write Totals line
                    sheet.merge_range(dep_raw_start, 0, dep_raw_start, 1, 'TOTALS', formats[1])
                    sheet.merge_range(dep_raw_start + 3, 0, dep_raw_start + 3, 1, 'TURNOVER', formats[1])
                    totals_col_start = month_col_start
                    totals_raw_start = dep_raw_start + 1
                    all_hired_cell = all_actually_resigned_cell = all_expiring_cell = False
                    for col in DATA_HEADER_LIST.keys():
                        cell_range = xl_range(7, totals_col_start, dep_raw_start, totals_col_start)
                        total_formula = '{=SUM(%s)}' % cell_range
                        sheet.write(totals_raw_start, totals_col_start, 'All ' + DATA_HEADER_LIST[col], formats[3])

                        sheet.write_formula(totals_raw_start + 1, totals_col_start, total_formula, formats[3])

                        if col == 'hired_count':
                            all_hired_cell = xl_rowcol_to_cell(totals_raw_start + 1, totals_col_start)
                        if col == 'actually_resigned_count':
                            all_actually_resigned_cell = xl_rowcol_to_cell(totals_raw_start + 1, totals_col_start)

                        if col == 'expiring_count':
                            all_expiring_cell = xl_rowcol_to_cell(totals_raw_start + 1, totals_col_start)

                        totals_col_start += 1

                        # write Turnover line
                        if totals_col_start == month_col_end + 1:
                            turn_over_formula = '{=%s/ (%s + %s)}' % (
                                all_hired_cell, all_actually_resigned_cell, all_expiring_cell)

                            sheet.merge_range(totals_raw_start + 2, month_col_start, totals_raw_start + 2,
                                              month_col_end, turn_over_formula, formats[4])

                    month_col_start = month_col_end + 1
            except Exception as e:
                print(e)

        else:
            sheet.merge_range(main_raw_start + 1, main_col_start, main_raw_end + 1, 20,
                              "There's No Data For This Year",
                              formats[2])

    def get_xlsx_report(self, data, response):
        period_range = self.get_period_range(data.get('form'))
        if not (data.get('form') or period_range):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        formats = self.set_format(workbook)
        # print each year data in single work sheet
        for p_range in period_range:
            sheet = workbook.add_worksheet(str(p_range['year']) + " Recruitment Detailed Report")
            self.sheet_writing(sheet, formats, p_range)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def print_report_xls(self):
        form = self.read()[0]
        self._test_dates_validation()
        data = {
            'ids': self.ids,
            'model': self._name,
            'record': self.id,
            'form': form,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'recruitment.detailed.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Recruitment Detailed Report',
                     },
            'report_type': 'xls'
        }
