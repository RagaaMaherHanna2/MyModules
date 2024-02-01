# -*- coding: utf-8 -*-
{
    'name': "ITQ Event Portal",
    'summary': "",
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
        'web',
        'base',
        'website',
        'portal',
        'itq_event_management',
    ],
    'data': [
        'data/website_menus.xml',

        'views/visit_request_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # JS
            'itq_event_portal/static/src/js/visitor_form.js',
            'itq_event_portal/static/src/js/visit_request_handler.js',

            # XML
            'itq_event_portal/static/src/xml/visitor_templates.xml',

        ],
    },
    'installable': True,
    'auto_install': False,
}
