# -*- coding: utf-8 -*-
import logging

from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request
from odoo.exceptions import AccessDenied
_logger = logging.getLogger(__name__)


class AuthSignupHomeDD(Home):

    @http.route()
    def web_login(self, *args, **kw):
        response = super(AuthSignupHomeDD, self).web_login(*args, **kw)
        if request.env.user.is_service_provider \
                or request.env.user.is_merchant \
                or request.env.user.is_sub_merchant \
                or request.env.user.is_accountant \
                or request.env.user.is_accountant_manager \
                or request.env.user.is_foodics_cashier :
            raise AccessDenied()
        return response
