# -*- coding: utf-8 -*-
{
    'name': "Itq Branch POS Warehouse Auto Generation",
    'version': "14.0.1.0.0",
    'summary': """ Auto generate POS or Warehouse stock when configure them from branch""",
    'description': """""",
    'author': "Itqan Systems",
    'company': "Itqan Systems",
    'maintainer': "Itqan Systems",
    'website': "https://cybrosys.com/",
    'depends': [
        'base',
        'update_me',
        'itq_branch_base',
        'itq_branch_stock_base',
        'itq_branch_pos',
        'point_of_sale_logo',
    ],
    'data': [
        'views/res_branch_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_config_views.xml',
    ],

    'license': "AGPL-3",
    'installable': True,
    'application': False
}
