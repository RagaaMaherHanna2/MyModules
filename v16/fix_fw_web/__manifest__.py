{
    'name': "ITQ Fix Framework Web",
    'summary': "",
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],

    'assets': {
        'web.assets_backend': [
            # 'fix_fw_web/static/src/views/form/form_label.js',
            'fix_fw_web/static/src/views/form/form_label.xml',
            'fix_fw_web/static/src/xml/form_error_dialog.xml',
            'fix_fw_web/static/src/xml/calendar_common_renderer.xml',
        ],
    },

    'installable': True,
    'auto_install': True,
    'application': False,
}
