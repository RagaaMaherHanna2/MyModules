# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ITQ Project Variable Wage',
    'description': """
        Project Variable Wage
    """,
    'sequence': 32,
    'depends': ['base', 'itq_contract_base', 'itq_salary_structure_base', 'itq_hr_payroll'],
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'data': [
        'security/ir.model.access.csv',

        'views/hr_contract_views.xml',
    ],
}
