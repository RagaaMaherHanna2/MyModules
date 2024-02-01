# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models


class ArchiveWarningWizard(models.TransientModel):
    _name = 'archive.warning.wizard'
    _description = "Archive Warning Wizard"

    def action_archive(self):
        self.env['work.procedure'].browse(self._context.get('active_id', [])).state = 'archived'
