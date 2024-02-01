# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Installment Company Management",
    "version": "14.0.0.1",
    "category": "Point of Sale",
    'summary': 'POS Installment Company Management',
    "description": """
    """,
    "author": "ItqanSystems",
    "website": "https://www.browseinfo.in",
    "currency": 'EUR',
    "depends": ['base', 'account',
                'point_of_sale',
                'pos_orders_all',
                ],
    "data": [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_payment_method_views.xml',
        'views/pos_config_views.xml',
        'views/installment_company_views.xml',
        'views/account_move_views.xml',
    ],
    "qweb": [
        'static/src/xml/pos_installment_pay_temps.xml',
    ],

    "auto_install": False,
    "installable": True,
}
