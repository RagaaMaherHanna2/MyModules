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
        'itq_hr_employee',
        'ks_dashboard_ninja',
    ],

    # always loaded
    'data': [
        # View files:
        'views/assets.xml',
        'views/my_dashboard_views.xml',

    ],
    'qweb': [
        'static/src/xml/my_dashboard_template.xml',
    ],
}
