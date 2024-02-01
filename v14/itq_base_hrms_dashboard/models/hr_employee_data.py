from odoo import fields, models, tools, api


class HrEmployeeData(models.Model):
    _name = "hr.employee.data"
    _description = "Hr Employee Data"
    _auto = False
    _rec_name = 'employee_id'

    gender = fields.Selection(
        [('male', "Male"), ('female', "Female")])
    citizenship = fields.Selection(
        [('citizen', "Citizen"), ('non_citizen', "Non-Citizen")])
    employee_state = fields.Selection([('new_hire', 'New-Hire'),
                                       ('onboarding', 'Onboarding'),
                                       ('active', 'Active'),
                                       ('pending_deactivation', 'Pending Deactivation'),
                                       ('extended', 'Extended'),
                                       ('termination_process', 'Termination Process'),
                                       ('under_review', 'Under Review'),
                                       ('inactive', 'Inactive'),
                                       ])
    is_citizen = fields.Boolean()
    country_id = fields.Many2one('res.country')
    religion_id = fields.Many2one(comodel_name="itq.employee.religion")
    employee_assigned_to = fields.Selection(selection=[('business_unit', 'Business Unit'),
                                                       ('project', 'Project')])
    employee_id = fields.Many2one('hr.employee')
    sponsor = fields.Selection(string="Sponsor",
                               selection=[('company', 'Company'), ('sister_company', 'Sister Company'),
                                          ('free', 'Free')])
    termination_type = fields.Many2one(comodel_name="itq.hr.termination.type")
    department_id = fields.Many2one('hr.department')
    terminated_date = fields.Date()
    hiring_date = fields.Date()
    age_avg = fields.Float()
    male_count = fields.Integer()
    female_count = fields.Integer()
    employees_count = fields.Integer()
    is_citizen_count = fields.Integer()

    def _select(self):
        return """
           SELECT 
                  row_number() OVER () as id,
                  EMP.id as employee_id,
                  EMP.state as employee_state,
                  EMP.employee_assigned_to as employee_assigned_to,
                  EMP.religion_id as religion_id,
                  EMP.country_id as country_id,
                  EMP.gender as gender,
                  EMP.department_id as department_id,
                  EMP.is_citizen as is_citizen,
                  EMP.sponsor as sponsor,
                  EMP.terminated_date as terminated_date,
                  EMP.hiring_date as hiring_date,
                  termination_type.id as termination_type,
                  CASE WHEN EMP.is_citizen = True THEN 'citizen' ELSE 'non_citizen' END as citizenship,
                  CASE WHEN EMP.gender = 'male' THEN count(EMP.id) ELSE 0 END as male_count,
                  CASE WHEN EMP.gender = 'female' THEN count(EMP.id) ELSE 0 END as female_count,
                  CASE WHEN EMP.is_citizen THEN count(EMP.id) ELSE 0 END as is_citizen_count,
                  count(EMP.id) as employees_count,
                  sum(EMP.employee_age)/ count(EMP.id) as age_avg
        """

    def _from(self):
        return """
            FROM 
                hr_employee AS EMP
        """

    def _join(self):
        return """
            LEFT JOIN itq_hr_termination_request AS termination_id ON  EMP.id = termination_id.employee_id and termination_id.state = 'terminated'
            LEFT JOIN itq_hr_termination_type AS termination_type ON  termination_type.id = termination_id.termination_type
        """

    def _where(self):
        return """ 
        where EMP.active = true
        """

    def _group_by(self):
        return """
            group by 
            EMP.id,
            EMP.employee_assigned_to,
            EMP.gender,
            EMP.religion_id,
            EMP.country_id,
            EMP.sponsor,
            EMP.terminated_date,
            EMP.hiring_date,
            termination_type.id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
