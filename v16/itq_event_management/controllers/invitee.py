import os
from odoo import http
from odoo.http import request
import pandas as pd


class InviteeController(http.Controller):

    @http.route('/web/binary/download_custom_excel', type='http', auth='user')
    def download_custom_excel(self, **kwargs):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        main_directory = os.path.dirname(os.path.dirname(current_directory))
        excel_file_path = os.path.join(main_directory, 'itq_event_management', 'templates', 'invitees.xlsx')
        df = pd.read_excel(excel_file_path)
        lang = request.env.context['lang'].partition('_')[0]

        if lang == 'ar':
            current_columns = ['اسم المدعو', 'الجوال', 'الجنسية', 'البريد الالكتروني', 'رقم الهوية']
        else:
            current_columns = ['Name', 'Mobile', 'Nationality', 'Email', 'Identification']

        df.columns = current_columns
        df.to_excel(excel_file_path, index=False)

        if os.path.exists(excel_file_path):
            with open(excel_file_path, 'rb') as file:
                excel_content = file.read()
            headers = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename=invitees.xlsx'),
            ]
            return request.make_response(excel_content, headers=headers)
        else:
            return request.not_found()
