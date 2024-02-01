{
    'name': "My Dashboard Leaves Transfer",

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
        'hr_holidays',
        'itq_hr_leave_transfer',
        'itq_my_hr_dashboard',
        'itq_my_dashboard_leaves',
    ],

    # always loaded
    'data': [
        # View files:
        'views/assets.xml',

    ],
    'qweb': [
        'static/src/xml/my_dashboard_leaves_allocation_template.xml',
    ],
}
