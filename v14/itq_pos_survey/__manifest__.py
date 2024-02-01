# -*- coding: utf-8 -*-
{
    'name': "Itq POS Survey",

    'summary': """
        Push survey through POS
    """,

    'description': """
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'Point Of Sale',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'survey',
        'point_of_sale',
        'itq_branch_base',
        'itq_auto_oe_chatter',
    ],

    # always loaded
    'data': [
        # Security files:
        "security/ir.model.access.csv",

        # View files:
        "views/survey_survey_views.xml",

    ],
    "qweb": [
        "static/src/xml/pos_receipt.xml"
    ],
}
