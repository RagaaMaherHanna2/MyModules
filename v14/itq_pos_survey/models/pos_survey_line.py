# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Survey(models.Model):
    _name = 'pos.survey.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'pos_id'

    survey_id = fields.Many2one('survey.survey', string="Survey")
    pos_id = fields.Many2one('pos.config', string="POS", tracking=True, required=True)
    date_from = fields.Date(string="From Date", tracking=True, required=True)
    date_to = fields.Date(string="To Date", tracking=True)
