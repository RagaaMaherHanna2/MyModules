{
    'name': "Project HRMS Dashboard",

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
        'itq_base_hrms_dashboard',
        'itq_hr_project',
    ],

    # always loaded
    'data': [
        # View files:
        'views/hrms_project_dashboard_details.xml',

    ],
}
