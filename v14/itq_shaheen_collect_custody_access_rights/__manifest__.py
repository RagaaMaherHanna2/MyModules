{
    'name': "collection Custody Access Rights",

    'summary': """collection Custody Access Rights """,

    'description': """collection Custody Access Rights""",

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'Uncategorized',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'itq_cheque_petty_cash_management',
        'hr',
    ],

    # always loaded
    'data': [
        # Security files:
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        # View files:
        'views/hr_employee_views.xml',
        'views/res_users_views.xml',

    ],
}
