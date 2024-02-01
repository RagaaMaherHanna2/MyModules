# -*- coding: utf-8 -*-
{
    'name': "Purchases Requisition Project",

    'summary': """
        Purchases Requisition Project
    """,

    'description': """
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'Uncategorized',

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'project',
        'itq_purchases_requisition',
        'itq_abstract_lookup_integration',
    ],

    # always loaded
    'data': [

        # View files:
        "views/purchase_requisition_project_views.xml",
        "views/project_task_view.xml",
        "views/project_project_view.xml",

    ],
}
