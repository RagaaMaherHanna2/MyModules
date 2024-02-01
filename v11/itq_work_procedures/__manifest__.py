# -*- coding: utf-8 -*-
{
    'name': "SEF - Working Procedures",

    'summary': "SEF - Working Procedures",

    'author': "ItqanSystems Company",

    'website': "http://www.itqansystems.com",

    'category': 'Human Resource',

    'version': '0.1',

    'depends': [
        'base',
        'mail',
        'web',
        'itq_basic',
        'itq_general_setting',
        'itq_emp_file',
        'itq_assets_management',
        'organization_chart',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',

        'views/approval_line_views.xml',
        'views/work_procedure_views.xml',
        'views/procedure_review_settings_views.xml',
        'views/procedure_confirm_settings_views.xml',
        'views/procedure_name_views.xml',
        'views/procedure_scope_views.xml',
        'views/documentation_committee_views.xml',
        'views/job_access_views.xml',
        'views/procedure_resource_views.xml',
        'views/procedure_document_views.xml',
        'views/notification_settings_views.xml',
        'views/itq_procedure_general_security_setting_view.xml',

        'reports/work_procedure_reports_templates.xml',
        'reports/work_procedure_reports_views.xml',
        'reports/actions_tracking_report_views.xml',

        'wizard/procedure_reports_wizard_views.xml',
        'wizard/actions_tracking_reports_wizard_views.xml',
        'wizard/archive_warning_wizard_views.xml',
        'data/data.xml',
        'assets.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
