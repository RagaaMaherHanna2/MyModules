# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ItqEventInstructionWizard(models.TransientModel):
    _name = 'itq.event.instruction.wizard'

    event_request_id = fields.Many2one(comodel_name='itq.event.request', ondelete='cascade', readonly=1)
    is_read_instruction = fields.Boolean(string='I Have Read Instructions')
    event_instructions = fields.Html(string="Events Instructions", readonly=True)

    def approve_button(self):
        self.ensure_one()
        self.event_request_id.send_under_review()
