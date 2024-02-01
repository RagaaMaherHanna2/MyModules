# -*- coding: utf-8 -*-
from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO


class Survey(models.Model):
    _inherit = 'survey.survey'
    # _inherit = ['survey.survey', 'itq.auto.oe.chatter']

    is_pos_survey = fields.Boolean(string="Push survey through POS")
    pos_survey_url = fields.Char(string="POS Survey URL")
    pos_survey_line_ids = fields.One2many('pos.survey.line', 'survey_id', string="POS Survey Lines")
