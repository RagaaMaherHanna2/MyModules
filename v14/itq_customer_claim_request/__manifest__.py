# -*- coding: utf-8 -*-
{
    'name': "Customer Claim Request",

    'summary': """
    """,

    'description': """
    """,
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'web',
        'base',
        'account',
        'point_of_sale',
        'itq_pos_installment_company_mgmt',
    ],

    # always loaded
    'data': [
        # data files:
        "data/sequence.xml",

        # Security files:
        "security/ir.model.access.csv",

        # View files:
        "views/customer_claim_request_views.xml",
        "reports/claim_report_report.xml",
        "wizards/rejection_wizard.xml",
    ],
}
