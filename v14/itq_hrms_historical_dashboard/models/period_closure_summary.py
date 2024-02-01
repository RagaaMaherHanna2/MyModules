from odoo import fields, models, tools


class PeriodClosureSummary(models.Model):
    _name = "period.closure.summary"
    _description = "Period Closure Summary"
    _auto = False
    _rec_name = 'period_closure_log_id'

    period_closure_log_id = fields.Many2one('itq.period.closure.log')
    period_line_id = fields.Many2one('itq.period.lines')
    from_date = fields.Date()
    to_date = fields.Date()
    average_age = fields.Integer()
    female_count = fields.Integer()
    male_count = fields.Integer()
    christian_count = fields.Integer()
    muslim_count = fields.Integer()
    other_religion_count = fields.Integer()
    business_unit_count = fields.Integer()
    project_unit_count = fields.Integer()
    citizen_count = fields.Integer()
    non_citizen_count = fields.Integer()
    sponsor_log_id = fields.Many2one('sponsor.details.log')
    country_log_id = fields.Many2one('nationality.details.log')
    department_log_id = fields.Many2one('department.details.log')

    def _select(self):
        return """
           SELECT 
                  row_number() OVER () as id,
                  LOG.id as period_closure_log_id,
                  LOG.period_line_id as period_line_id,
                  LOG.average_age as average_age,
                  LOG.female_count as female_count,
                  LOG.male_count as male_count,
                  LOG.christian_count as christian_count,
                  LOG.muslim_count as muslim_count,
                  LOG.other_religion_count as other_religion_count,
                  LOG.business_unit_count as business_unit_count,
                  LOG.project_unit_count as project_unit_count,
                  LOG.citizen_count as citizen_count,
                  LOG.non_citizen_count as non_citizen_count,
                  period_line_id.from_date as from_date,
                  period_line_id.to_date as to_date,
                  nationality_log_id.id as country_log_id,
                  sponsor_log_id.id as sponsor_log_id,
                  department_log_id.id as department_log_id
                  
        """

    def _from(self):
        return """
            FROM 
                itq_period_closure_log AS LOG
        """

    def _join(self):
        return """
            LEFT JOIN itq_period_lines AS period_line_id ON period_line_id.id = LOG.period_line_id
            LEFT JOIN nationality_details_log AS nationality_log_id ON nationality_log_id.period_closure_log_id = LOG.id
            LEFT JOIN sponsor_details_log AS sponsor_log_id ON sponsor_log_id.period_closure_log_id = LOG.id
            LEFT JOIN department_details_log AS department_log_id ON department_log_id.period_closure_log_id = LOG.id
        """

    # LEFT
    # JOIN
    # project_termination_log
    # AS
    # project_termination_log
    # ON
    # period_closure_log_id.id = LOG.id
    # LEFT
    # JOIN
    # department_termination_log
    # AS
    # department_termination_log
    # ON
    # period_closure_log_id.id = LOG.id

    def _where(self):
        return """ 
        """

    def _group_by(self):
        return """
            group by 
            LOG.id,
            period_line_id.id,
            nationality_log_id.id,
            sponsor_log_id.id,
            department_log_id.id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query= """
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by())
        print(query)
        self._cr.execute(query)
