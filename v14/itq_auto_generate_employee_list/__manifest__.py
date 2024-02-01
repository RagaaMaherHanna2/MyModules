# -*- coding: utf-8 -*-
{
    'name': "Auto Generate Employee List",

    'summary': """
    """,

    'description': """
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'Uncategorized',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'itq_payroll_base',
        'itq_hr_project',
    ],

    # always loaded
    'data': [
        # Data files:
        "data/default_employee_list.xml",

        # Views files:
        "views/res_config_settings_views.xml",
    ],
}
