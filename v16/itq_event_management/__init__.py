# -*- coding: utf-8 -*-
from . import abstract_models
from . import models
from . import wizards
from . import controllers
from odoo import api, SUPERUSER_ID


def _post_init_make_days(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['itq.day.line'].create_day_line()