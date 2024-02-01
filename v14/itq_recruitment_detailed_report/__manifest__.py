{
    'name': "Recruitment Detailed Report",

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
        'hr_recruitment',
        'itq_recruitment_plan',
        'itq_contract_base',
        'itq_end_of_service',
    ],

    # always loaded
    'data': [
        # Security files:
        'security/recruitment_detailed_dashboard_groups.xml',
        'security/ir.model.access.csv',

        # View files:
        'wizard/recruitment_detailed_views.xml',

    ],
}
