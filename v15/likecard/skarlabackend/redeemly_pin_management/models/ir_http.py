# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re
from odoo.exceptions import UserError

from odoo import SUPERUSER_ID, api, models, registry as registry_get
from odoo.http import request
from odoo.addons.auth_jwt.exceptions import(
    UnauthorizedMalformedAuthorizationHeader,
    UnauthorizedMissingAuthorizationHeader,
    UnauthorizedSessionMismatch,
)

_logger = logging.getLogger(__name__)

AUTHORIZATION_RE = re.compile(r"^Bearer ([^ ]+)$")


class IrHttpJwt(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_jwt(cls, validator_name=None):
        assert request.db
        assert not request.uid
        assert not request.session.uid
        token = cls._get_bearer_token()

        assert token
        registry = registry_get(request.db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            validator = env["auth.jwt.validator"]._get_validator_by_name(validator_name)
            assert len(validator) == 1
            payload = validator._decode(token)
            uid = validator._get_and_check_uid(payload)

            # _token = env["api.access_token"].sudo()
            # access_token = _token.search(
            #     [('token', '=', token)]
            # )
            # if len(access_token) > 0:
            #     if access_token.logout == True:
            #         raise UserError("Expired TOken")

            # if uid != :
            #     _logger.info("Missing Authorization header.")
            #     raise UnauthorizedMissingAuthorizationHeader()

            assert uid
            partner_id = validator._get_and_check_partner_id(payload)

        request.uid = uid  # this resets request.env
        # user = request.env['res.users'].browse(uid).sudo()
        # request.session.uid = uid
        # request.session.login = user
        # request.session.session_token = uid
        # request.session.context = dict(request.env['res.users'].context_get() or {})
        # request.session.context['uid'] = uid
        # request.session._fix_lang(request.session.context)
        # context = request.env.context.copy()
        # context.update({'lang': request.session['context']['lang']})
        # request.env.context = context

        request.jwt_payload = payload
        request.jwt_partner_id = partner_id

    @classmethod
    def _get_bearer_token(cls):
        # https://tools.ietf.org/html/rfc2617#section-3.2.2
        authorization = request.httprequest.environ.get("HTTP_AUTHORIZATION")
        if not authorization:
            _logger.info("Missing Authorization header.")
            raise UnauthorizedMissingAuthorizationHeader()
        # https://tools.ietf.org/html/rfc6750#section-2.1
        mo = AUTHORIZATION_RE.match(authorization)
        if not mo:
            _logger.info("Malformed Authorization header.")
            raise UnauthorizedMalformedAuthorizationHeader()
        return mo.group(1)
