from odoo import http, SUPERUSER_ID , _
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools.config import config

from odoo.addons.redeemly_utils.controllers.base_controller import BaseController

class WebsiteApiKeyController(BaseController):

    @http.route(
        "/exposed/generate_website_key",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def generate_website_key(self, **kw):
        user = request.env.user
        if not user or not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {
                "website_name": "required|string",
            },
        )
        website_key = request.env['website.api.key'].sudo().create({
            'name': validated.get('website_name'),
            'user_id': user.id
        })
        validated.update({
            'website_redeemly_api_key': website_key.website_redeemly_api_key,
            'user_id': website_key.user_id.id
        })
        return BaseController._create_response(validated)



    @http.route(
        "/exposed/get_sp_websites_keys",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def get_sp_websites_keys(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {
                "offset": "number",
                "limit": "number",
                "website_name": "string"
            },
        )
        user = request.env.user
        if not user.is_service_provider:
            raise AccessDenied()
        limit = validated.get('limit') if validated.get('limit') else 20
        offset = validated.get('offset') if validated.get('offset') else 0

        domain = [('user_id', '=', user.id)]

        if validated.get('website_name'):
            domain.append(('name', 'ilike', validated.get('website_name')))

        data = request.env['website.api.key'].sudo().search(domain, limit=limit, offset=offset)
        count = request.env['website.api.key'].sudo().search_count(domain)
        result = [item.serialize_for_api() for item in data]
        return BaseController._create_response({"data": result, "totalCount": count}, message='')
