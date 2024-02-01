# -*- coding: utf-8 -*-
{
    'name': "ITQ Project Task Assignation",

    'summary': """
        ITQ Project Task Assignation
    """,

    'description': """
        ITQ Project Task Assignation
    """,

    'author': "Itqan Systems",

    'website': "http://www.itqansystems.com",

    'category': 'project',

    'version': '0.1',

    'depends': [
        'hr_timesheet',
        'project',
        'itq_project_management',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml'
    ],
}
