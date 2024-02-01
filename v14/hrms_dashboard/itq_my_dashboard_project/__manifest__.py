{
    'name': "My Dashboard Projects",

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
        'itq_my_hr_dashboard',
        'itq_hr_project',
    ],

    # always loaded
    'data': [
        # View files:
        'views/assets.xml',

    ],
    'qweb': [
        'static/src/xml/my_dashboard_Projects_template.xml',
    ],
}
