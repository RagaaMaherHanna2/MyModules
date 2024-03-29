# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ITQ Deferred Expense Revenue ',
    'description': """
ITQ Deferred Expense Revenue 
=================
Manage assets owned by a company or a person.
Keeps track of depreciations, and creates corresponding journal entries.

    """,
    'category': 'Accounting/Accounting',
    'sequence': 32,
    'depends': ['itq_account_base'],
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/account_asset_views.xml',
        'views/account_deferred_revenue.xml',
        'views/account_deferred_expense.xml',
        'views/account_move_views.xml',
        'views/account_asset_templates.xml',
    ],
    'qweb': [
        "static/src/xml/account_asset_template.xml",
    ],
}
