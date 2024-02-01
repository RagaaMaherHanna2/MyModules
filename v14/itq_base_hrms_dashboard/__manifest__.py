{
    'name': "Base HRMS Dashboard",

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
        'itq_hr_employee',
        'itq_end_of_service',
        'itq_service_base',
    ],

    # always loaded
    'data': [
        # Security files:
        'security/hrms_dashboard_security_groups.xml',
        'security/ir.model.access.csv',

        # View files:
        'views/assets.xml',
        'views/hrms_dashboard_details.xml',

    ],
}
