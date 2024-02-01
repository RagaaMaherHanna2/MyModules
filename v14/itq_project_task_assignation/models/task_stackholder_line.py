from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TaskStackholderLine(models.Model):
    _name = 'task.stackholder.line'
    _description = 'Task Stackholder Line'
    _rec_name = 'employee_id'

    task_id = fields.Many2one('project.task', string='Task')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one(related='employee_id.job_id', string='Jop Position')
    country_id = fields.Many2one(related='employee_id.country_id', string='Country')
    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date')

    # @api.constrains('task_id', 'date_start', 'date_end')
    # def check_dates_validations(self):
    #     for rec in self:
    #         if rec.date_start and rec.date_end and rec.task_id:
    #             print(rec.date_start,  rec.task_id.start_date, rec.date_end, rec.task_id.date_end)
    #             if rec.date_start < rec.task_id.start_date or rec.date_end > rec.task_id.date_end:
    #                 raise ValidationError(_("Stackholder dates must be within task start and end dates!"))
