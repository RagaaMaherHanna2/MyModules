# -*- coding: utf-8 -*-
{
    'name': "Sample/Gift Request POS",

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
        'point_of_sale',
        'itq_sample_gift_request',
    ],

    # always loaded
    'data': [
        # security files:
        "security/ir.model.access.csv",


        # Root menu items files:

        # View files:
        "views/sample_gift_request_views.xml",

    ],
}
