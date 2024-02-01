# -*- coding: utf-8 -*-
{
    'name': "ITQ Debranding Portal",
    'summary': "",
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
    	'portal',
    	'itq_debranding',
    ],
    'data': [
        # Security

        # Views
        'views/portal_templates.xml',

    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
