# -*- coding: utf-8 -*-
{
    'name': "Sample/Gift Request",

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
        'base',
        'stock',
        'itq_branch_base',
        'itq_branch_stock_base',
        'itq_branch_product_base',
        'itq_branch_employee_base',
    ],

    # always loaded
    'data': [
        # data files:
        "data/sequence.xml",

        # Security files:
        "security/sample_gift_request_security.xml",
        "security/ir.model.access.csv",

        # View files:
        "views/sample_gift_request_views.xml",
        "views/res_branch_views.xml",
        "views/product_views.xml",
        "views/sample_gift_line_views.xml",
        "wizards/rejection_wizard_views.xml",
    ],
}
