{
    'name': "My Dashboard Benefits",

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
        'itq_contract_base',
        'itq_contract_benefit_change',
        'itq_non_periodical_benefit_request',
    ],

    # always loaded
    'data': [
        # View files:
        'views/assets.xml',

    ],
    'qweb': [
        'static/src/xml/my_dashboard_benefits_template.xml',
    ],
}
