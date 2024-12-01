from datetime import datetime

from odoo.http import route
import json
from odoo.http import request
from odoo.tools import config
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT


class WhiteLabellingController(BaseController):
    # @route("/exposed/craete_sp",
    #        type="json",
    #        auth="jwt_dashboard",
    #        save_session=False,
    #        cors=config.get('control_panel_url'))
    # @BaseController.with_errors
    # def create_sp(self, **kw):
    #     user_data = BaseController.get_validated(
    #         kw,
    #         {
    #             "name": "string|required",
    #             "white_labeling":"string",
    #             "login": "string|required",
    #             "image": "image",
    #             'is_service_provider': "boolean",
    #         },
    #     )
    #
    #     if BaseController.is_valid_url(user_data.get("image")):
    #         user_data["image_url"] = user_data.pop("image")
    #     else:
    #         user_data["image_1920"] = user_data.pop("image")
    #     user_data["is_service_provider"] = True
    #
    #     user_data["sel_groups_1_9_10"] = 9
    #
    #     if not user_data['white_labeling'] :
    #         user_data['white_labeling'] = user_data["login"]
    #
    #     user = request.env['res.users'].with_user(1).create(user_data)
    #
    #     return BaseController._create_response(user.serialize_for_api())

    @route("/exposed/auth/profile",
           type="json",
           auth="none",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_profile(self, **kw):
        key = kw.get("sp_hash")
        sku = kw.get("sku")
        user = request.env['res.users'].with_user(1).search([
            ('sp_hash' , '=' , key)
        ])
        if not user:
            raise UserError("Invalid Hash")

        if sku:
            product = request.env['product.template'].with_user(1).search([('SKU', '=', sku),
                                                                           ('service_provider_id', '=', user.id)
                                                                           ])
            if not product:
                raise UserError("Invalid Product")
            attributes = product.serialize_for_api_profile()
        else:
            attributes = []
        result = {
            'user': user.partner_id.serialize_for_api(),
            'product_attributes': attributes,
            'codes_additional_value': user.codes_additional_value
        }
        return BaseController._create_response(result)