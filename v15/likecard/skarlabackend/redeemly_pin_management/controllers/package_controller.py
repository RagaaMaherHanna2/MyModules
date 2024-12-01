from datetime import datetime

from odoo.http import route
import json
from odoo.http import request
from odoo.tools import config
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT

from odoo.addons.redeemly_pin_management.services.notification_service import NotificationService

class PackageController(BaseController):
    @route("/exposed/create_package",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_package(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        package_data = BaseController.get_validated(
            kw,
            {
                "package_name": "string|required",
                "package_name_ar": "string|required",
                # "code_type": "string",
                # "code_seperator": "string",
                # "code_hours_duration": "number",
                # "code_days_duration": "number",
                "expiry_date": "string"
            },
            req_only=True
        )
        package_data["service_provider_id"] = request.uid
        package_data["expiry_date"] = (
            datetime.strptime(package_data["expiry_date"], DATETIME_FORMAT)
            if package_data["expiry_date"]
            else False
        )
        package = request.env['package'].with_user(1).create(package_data)

        return BaseController._create_response(package.serialize_for_api())

    @route("/exposed/edit_package",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def edit_package(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        package_data = BaseController.get_validated(
            kw,
            {
                "reference": "string|required",
                "package_name": "string|required",
                "package_name_ar": "string|required",
                # "code_type": "string",
                # "code_seperator": "string",
                # "code_hours_duration": "number",
                # "code_days_duration": "number",
                "expiry_date": "string",
                "state": "string"
            },
            req_only=True
        )
        package_data["service_provider_id"] = request.uid
        package_data["expiry_date"] = (
            datetime.strptime(package_data["expiry_date"], DATETIME_FORMAT)
            if package_data["expiry_date"]
            else False
        )
        product_reference = package_data.pop("reference")
        package = request.env['package'].with_user(1).search([
            ("name", "=", product_reference),
            ("service_provider_id", '=', request.uid)
        ])
        if not package:
            raise UserError("Package Not Found")
        package.write(package_data)
        return BaseController._create_response(package.serialize_for_api())

    @route("/exposed/list_packages",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def list_packages(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"package_name": "string", "offset": "int", "limit": "int", "reference": "string", "state": "string"},
        )
        domain = [('service_provider_id', '=', request.uid)]
        package_name = validated.get("package_name")
        reference = validated.get("reference")
        state = validated.get("state")
        offset = validated.get('offset')
        limit = validated.get("limit")
        if package_name:
            domain += ["|", ('package_name', 'ilike', package_name), ("package_name_ar", 'ilike', package_name)]
        if state:
            domain += [("state", '=', state)]
        if reference:
            domain += [('name', '=', reference)]
        packages = request.env['package'].with_user(1).search(domain, limit=limit, offset=offset,
                                                              order="create_date desc")
        packages_count = request.env['package'].with_user(1).search_count(domain)
        data = []
        for p in packages:
            data.append(p.serialize_for_api(populate=bool(reference)))
        res = {'data': data, 'totalCount': packages_count}
        return BaseController._create_response(res)

    @route("/exposed/add_generation_request",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def add_generation_request(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        generation_data = BaseController.get_validated(
            kw,
            {
                "package": "string|required",
                "lines": "list|required"
            },
            req_only=True
        )
        lines = []
        for line in generation_data['lines']:
            validated = BaseController.get_validated(
                line,
                {
                    "product": "number|required",
                    "quantity": "number|required"
                },
                req_only=True
            )
            lines.append(validated)

        if len(lines) == 0:
            raise UserError("Lines Are Empty")

        package = request.env['package'].with_user(1).search([
            ("name", "=", generation_data['package']),
            ("service_provider_id", '=', request.uid)
        ])
        if not package:
            raise UserError("Package Not Found")

        lines_data = []
        for line in lines:
            product = request.env['product.template'].with_user(1).search([
                ("id", "=", line['product']),
                ("service_provider_id", '=', request.uid)
            ])
            if not product:
                raise UserError(f"Product {line['product']} Not Found")
            if line['quantity'] < 0 or line['quantity'] > 50000:
                raise UserError(f"Invalid Quantity")
            lines_data.append((0, 0, {
                "product": product.id,
                "quantity": line['quantity']
            }))

        generation_request = request.env['package.generation.request'].with_user(1).create({
            "package": package.id,
            "lines": lines_data
        })

        return BaseController._create_response(generation_request.serialize_for_api(), 200,
                                               "Generation Request Submitted Successfully .")

    @route("/exposed/cancel_generation_request",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def cancel_generation_request(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {
                "id": "number|required"},
            req_only=True
        )
        generation_request = request.env['package.generation.request'].with_user(1).search([
            ("id", "=", validated['id']),
        ])
        if not generation_request or generation_request.package.service_provider_id.id != user.id:
            raise UserError("Not Found")

        if generation_request.state != "pending":
            raise UserError('Generation Cannot Be Canceled')

        generation_request.write({
            "state": "canceled"
        })
        return BaseController._create_response(generation_request.serialize_for_api(), 200,
                                               "Generation Request Canceled Successfully .")

    @route("/exposed/merchant_package_invite",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def merchant_package_invite(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        invite_data = BaseController.get_validated(
            kw,
            {
                "product": "id|required",
                "merchant": "string|required",
                "limit": "number",
                "price": "number|required",
                "unlimited": "boolean",
                "tax_id":"number"
            },
            req_only=True
        )

        product = request.env['product.template'].with_user(1).search([
            ("id", "=", invite_data['product']),
            ("service_provider_id", '=', request.uid)
        ])

        if not product:
            raise UserError("Product Not Found")

        merchant = request.env['res.users'].with_user(1).search([
            ("reference", "=", invite_data['merchant']),
            ("is_merchant", '=', True),
        ])

        if not merchant:
            raise UserError("Merchant Not Found")

        already_invited = request.env['merchant.package.invites'].with_user(1).search([
            ("merchant", '=', merchant.id),
            ("product", '=', product.id),
        ])

        if already_invited:
            raise UserError("Merchant Already Invited")

        invitation_to_another_sp = request.env['merchant.package.invites'].with_user(1).search_count([
            ("merchant", '=', merchant.id),
            ("product.service_provider_id", '!=', request.uid),
        ])

        if invitation_to_another_sp > 0:
            raise UserError("Already Invited To Another Service Provider")
        if invite_data.get('tax_id'):
            tax = request.env['account.tax'].with_user(1).search_count([
                ("id", "=", invite_data['tax_id']),
                ("service_provider_id", '=', request.uid)
            ])
            if not tax:
                raise UserError("Tax Not Found")

        invite_data['merchant'] = merchant.id
        invite_data['product'] = product.id
        invite = request.env['merchant.package.invites'].with_user(1).with_context(tracking_disable=True).create(invite_data)

        NotificationService.Send_Notification_email(request.env.user, invite)

        return BaseController._create_response(invite.serialize_for_api(), 200, "Merchant Invited Successfully .")

    @route("/exposed/merchant_package_invite_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def merchant_package_invite_list(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        if not kw.get("invites"):
            raise UserError("Missing invites array")

        invites = []
        for invite in kw.get("invites"):
            invite_data = BaseController.get_validated(
                invite,
                {
                    "product": "id|required",
                    "merchant": "string|required",
                    "limit": "number",
                    "price": "number|required",
                    "unlimited": "boolean"
                },
                req_only=True
            )

            product = request.env['product.template'].with_user(1).search([
                ("name", "=", invite_data['product']),
                ("service_provider_id", '=', request.uid)
            ])

            if not product:
                raise UserError(f"product {invite_data['product']} Not Found")

            merchant = request.env['res.users'].with_user(1).search([
                ("reference", "=", invite_data['merchant']),
                ("is_merchant", '=', True)
            ])

            if not merchant:
                raise UserError(f"Merchant {invite_data['merchant']} Not Found")

            already_invited = request.env['merchant.package.invites'].with_user(1).search([
                ("merchant", '=', merchant.id),
                ("product", '=', product.id),
            ])

            if already_invited:
                raise UserError(f"Merchant {already_invited.merchant.name} Already Invited")

            invite_data['merchant'] = merchant.id
            invite_data['product'] = product.id
            invites.append(invite_data)
        created_invites = request.env['merchant.package.invites'].with_user(1).create(invites)



        result = [invite.serialize_for_api() for invite in created_invites]



        return BaseController._create_response(result, 200, "Merchant Invited Successfully .")

    @route("/exposed/edit_merchant_package_invite",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def edit_merchant_package_invite(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        invite_data = BaseController.get_validated(
            kw,
            {
                "id": "number|required",
                "quantity": "number",
                "price": "number",
                'enabled': "boolean",
                "unlimited": "boolean"
            },
            req_only=True
        )
        quantity = invite_data.get('quantity') if invite_data.get('quantity') else 0

        invite = request.env['merchant.package.invites'].with_user(1).search([('id', '=', invite_data['id'])])

        if invite.product.service_provider_id.id != user.id:
            raise UserError("Invite Not Found")

        invite.limit += quantity
        if invite.limit < 0:
            invite.limit = 0

        invite_data.pop('id')
        if invite_data.get('quantity'):
            invite_data.pop('quantity')

        invite.write(invite_data)

        return BaseController._create_response(invite.serialize_for_api(), 200, "Merchant Invite Updated.")

    @route("/exposed/get_merchant_products",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_merchant_products(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        return self.get_merhchant_products_func(kw, user)

    @route("/exposed/get_merchant_products_online",
           type="json",
           auth="none",
           save_session=False,
           cors='*')
    @BaseController.with_errors
    def get_merchant_products_online(self, **kw):
        user = BaseController.key_authenticate(kw)
        return self.get_merhchant_products_func(kw, user)

    @staticmethod
    def get_merhchant_products_func(kw, user):
        if not user.is_merchant:
            raise AccessDenied()

        validated = BaseController.get_validated(
            kw,
            {"offset": "int", "limit": "int", "name": "string", "id": "number", "product_specific_attribute": "string"},
        )
        offset = validated.get('offset')
        limit = validated.get("limit")
        name = validated.get("name")
        id = validated.get("id")
        product_specific_attribute = validated.get('product_specific_attribute')
        if user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["1.1"], user=user)
            domain = [
                ('merchant', '=', user.parent_merchant.id),
                ("enabled", '=', True)
            ]
        else:
            domain = [
                ('merchant', '=', user.id),
                ("enabled", '=', True)
            ]
        if name:
            domain.append(('product.name', 'ilike', name))
        if id:
            domain.append(('id', '=', id))
        if product_specific_attribute:
            domain.append(('product.product_specific_attribute', '=', product_specific_attribute))
        invites = request.env['merchant.package.invites'].with_user(1).search(domain, limit=limit, offset=offset)
        res = [
            invite.serialize_for_api(id)
            for invite in invites
        ]

        package_count = request.env['merchant.package.invites'].with_user(1).search_count(domain)

        return BaseController._create_response({'data': res, 'totalCount': package_count})

    @route("/exposed/get_sp_invite_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_sp_invite_list(self, **kw):
        user = request.env.user
        if not (user.is_service_provider or user.is_accountant_manager):
            raise AccessDenied()

        validated = BaseController.get_validated(
            kw,
            {"id": "number", "limit": "number", "offset": "number", "service_provider_id": "number"},
        )
        id = validated.get("id")
        limit = validated.get("limit") if validated.get("limit") else 20
        offset = validated.get("offset") if validated.get("offset") else 0
        if user.is_service_provider:
            domain = [
                ('invites_ids.product.service_provider_id', '=', user.id),
                ("invites_ids.enabled", '=', True),
                ('is_merchant', '=', True)
            ]
        else:
            domain = [
                ('invites_ids.product.service_provider_id', '=', validated['service_provider_id']),
                ('is_merchant', '=', True)
            ]
        if id:
            domain.append(('merchant.id', '=', id))
        merchants = request.env['res.users'].with_user(1).search(domain, limit=limit, offset=offset)
        data = []
        for merchant in merchants:
            item = {
                'id': merchant.id,
                'name': merchant.name,
                'reference': merchant.reference,
                "all_merchant_invitations": []
            }
            for invite in merchant.invites_ids.filtered(lambda v: v.product.service_provider_id.id == user.id):
                item['all_merchant_invitations'].append(invite.serialize_for_api(id=invite.id))
            data.append(item)
        count = request.env['res.users'].with_user(1).search_count(domain)

        return BaseController._create_response({'data': data, 'totalCount': count})

    @route("/exposed/list_package_merchant_invites",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def list_package_merchant_invites(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()
        invite_data = BaseController.get_validated(
            kw,
            {
                "id": "number",
                "limit": "number",
                "price": "float",
                "expiry_date": "string",
                'enabled': "boolean",
                'package': "string"
            },
            req_only=True
        )
        reference = invite_data.get("package")
        offset = invite_data.get('offset')
        limit = invite_data.get("limit")
        id = invite_data.get("id")
        domain = []
        if reference:
            domain = [('package.name', '=', reference)]
        if id:
            domain.append(('id', '=', id))
        if domain == []:
            raise UserError('Id or package required')
        invites = request.env['merchant.package.invites'].with_user(1).search(domain, limit=limit, offset=offset)
        invites_count = request.env['merchant.package.invites'].with_user(1).search_count(domain)
        data = []
        for p in invites:
            data.append(p.serialize_for_api())
        res = {'data': data, 'totalCount': invites_count}
        return BaseController._create_response(res)

    @route("/exposed/get_package_codes",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_package_codes(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        validated = BaseController.get_validated(
            kw,
            {"offset": "int", "limit": "int", "reference": "string|required", "status": "list", "product": "list", "name": "string"},
        )
        offset = validated.get('offset')
        limit = validated.get("limit")
        reference = validated.get("reference")
        status = validated.get("status")
        products = validated.get("product")
        name = validated.get("name")
        domain = [('package.name', '=', reference)]
        if status:
            domain.append(("status", 'in', status))
        if products:
            domain.append(("product", 'in', products))
        if name:
            domain.append(("name", 'ilike', name))
        if user.is_merchant:
            domain.append(("pulled_by", '=', user.id))
        if user.is_service_provider:
            domain.append(("package.service_provider_id", '=', user.id))
        codes = request.env['package.codes'].with_user(1).search(domain, limit=limit, offset=offset)
        res = [
            code.serialize_for_api()
            for code in codes
        ]

        codes_count = request.env['package.codes'].with_user(1).search_count(domain)

        return BaseController._create_response({'data': res, 'totalCount': codes_count})

    @route("/exposed/get_package_products",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_package_products(self, **kw):
        user = request.env['res.users'].with_user(1).search([('id', '=', request.uid)])
        if not user.is_service_provider:
            raise AccessDenied()

        validated = BaseController.get_validated(
            kw,
            {"reference": "string|required"},
        )
        reference = validated.get("reference")
        domain = [
            ('name', '=', reference),
        ]
        generation_requests = request.env['package'].with_user(1).search(domain).generation_requests
        products = []
        for generation_request in generation_requests:
            for product in generation_request.lines.product:
                products.append(product)
        res = [
            {
                "id": product.id,
                "name": product.name
            }
            for product in products
        ]

        return BaseController._create_response({'data': res})
