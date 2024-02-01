# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    qr_code = fields.Binary("QR Code", attachment=True)

    def generate_qr_code(self, pos_survey_url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(pos_survey_url)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        return qr_image

    def get_pos_survey(self, pos_id):

        today = fields.Date.today()
        pos_survey_line = self.env['pos.survey.line'].search([
            ('pos_id', '=', int(pos_id)),
            ('date_from', '<=', today),
            ('date_to', '>=', today),
        ])
        survey_url = pos_survey_line.survey_id.pos_survey_url or ''
        return {
            'survey_qr': self.generate_qr_code(survey_url),
            'survey_url': survey_url
        }

