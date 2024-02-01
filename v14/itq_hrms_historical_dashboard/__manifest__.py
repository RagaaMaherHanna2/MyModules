{
    'name': "HRMS Historical Dashboard",

    'summary': """
    """,

    'description': """
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'hr',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'web_dashboard',
        'itq_hr_base',
        'itq_period_closure',
    ],

    # always loaded
    'data': [
        # Security files:
        # 'security/hrms_historical_dashboard_security_group.xml',
        # 'security/ir.model.access.csv',

        # View files:
        'views/period_closure_log_dashboard.xml',

    ],
}
