# -*- coding: utf-8 -*-
{
    'name': "ITQ Event Management",
    'summary': "",
    'author': "Itqan Systems",
    'website': "http://www.itqansystems.com",
    'version': '0.1',
    'license': 'LGPL-3',
    'post_init_hook': '_post_init_make_days',
    'depends': [
        'web',
        'base',
        'hr',
        'mail',
        'itq_track_m2m',
    ],
    'data': [

        # Security:
        'security/res_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',

        # Reports:
        'report/event_request_report.xml',
        'report/event_permission_report.xml',

        # Data:
        'data/itq_event_management_settings_data.xml',
        'data/ir_sequence.xml',
        'data/itq_attraction_location.xml',

        # Wizards:
        'wizards/itq_return_event_request.xml',
        'wizards/itq_reject_event_request.xml',
        'wizards/itq_event_instruction_wizard.xml',
        'wizards/itq_invitee.xml',
        'wizards/itq_permission_invitee_wizard.xml',

        # Views:
        'views/itq_event_type_view.xml',
        'views/itq_holding_branch_views.xml',
        'views/hr_department_view.xml',
        'views/itq_catering_type_view.xml',
        'views/itq_event_organizer_view.xml',
        'views/itq_event_management_settings_view.xml',
        'views/itq_organizer_member_view.xml',
        'views/itq_attraction_location.xml',
        'views/itq_event_seating_type.xml',
        'views/itq_target_audience.xml',
        'views/itq_amenity_specification.xml',
        'views/itq_day_line.xml',
        'views/itq_event_request.xml',

        'views/itq_event_request_review.xml',
        'views/itq_event_request_reject.xml',
        'views/itq_event_request_approve.xml',
        'views/itq_entrance_configuration.xml',
        'views/itq_event_permission.xml',

        # Visit Request
        'views/itq_visit_request_view.xml',
        # Visit Request Configuration
        'views/itq_visit_classification_view.xml',
        'views/itq_organization_type_view.xml',
        'views/itq_research_type_view.xml',
        'views/itq_documentation_type_view.xml',

        # Templates:
        'templates/notify_department_manager_mail_template.xml',
        'templates/notify_creator_mail_template.xml',
        'templates/visit_request_mail_templates.xml',

        # Menus:
        'menus.xml',
    ],
    'external_dependencies': {
        'python': ['phonenumbers', 'pandas', 'openpyxl'],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
