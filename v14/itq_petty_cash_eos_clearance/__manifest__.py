{
    'name': "Petty Cash EOS Clearance",

    'summary': """
    Petty Cash EOS Clearance
    """,

    'description': """
    Petty Cash EOS Clearance
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'Uncategorized',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'itq_hr_employee',
        'itq_end_of_service',
        'itq_petty_cash_management',
    ],

    # always loaded
    'data': [
        # Data files:
        'data/petty_cash_checklist.xml',

    ],
}
