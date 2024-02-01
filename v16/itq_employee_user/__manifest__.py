# -*- coding: utf-8 -*-
{
    'name': "ITQ Employee User",
    'summary': "",
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        # Views:
        'views/res_users_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
