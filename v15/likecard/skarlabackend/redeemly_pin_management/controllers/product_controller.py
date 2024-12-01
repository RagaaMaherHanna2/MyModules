import uuid
from datetime import datetime, timezone
import requests

from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT, DATE_FORMAT
from odoo.http import route, content_disposition
import json
from odoo.http import request
from odoo.tools import config
from odoo.addons.redeemly_utils.controllers.base_controller import BaseController
from odoo.exceptions import UserError, AccessDenied, ValidationError
from odoo.addons.redeemly_pin_management.services.code_validation_service import RedeemlyCodeValidationService
from odoo.addons.redeemly_pin_management.services.redeem_service import RedeemService
from odoo import _, SUPERUSER_ID
from odoo.tools.safe_eval import pytz


class ProductController(BaseController):
    @route("/exposed/list_products",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_product_list(self, **kw):
        if not (request.env.user.is_service_provider or request.env.user.is_sp_finance):
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"name": "string", "offset": "int", "limit": "int", "product_id": "number", "category_name": "string"},
        )
        service_provider_id = request.uid if request.env.user.is_service_provider else request.env.user.finance_service_provider_id.id

        domain = [('service_provider_id', '=', service_provider_id), ("is_redeemly_product", "=", True)]
        name = validated.get("name")
        product_id = validated.get("product_id")
        category_name = validated.get("category_name")
        offset = validated.get('offset')
        limit = validated.get("limit")
        if name:
            domain += ["|", ('name', 'ilike', name), ("name_ar", 'ilike', name)]
        if product_id:
            domain += [('id', '=', product_id)]
        if category_name:
            domain += ["|", ('categ_id.name', 'ilike', category_name), ("categ_id.name_ar", 'ilike', category_name)]
        products = request.env['product.template'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                       order="create_date desc")
        totalCount = request.env['product.template'].with_user(1).search_count(domain)
        data = [p.serialize_for_api(product_id) for p in products]
        res = {'data': data, 'totalCount': totalCount}
        return BaseController._create_response(res)

    @route("/exposed/get_product_name_by_id",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_product_name_by_id(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"product_id": "number"},
        )
        if not request.env.user.is_service_provider and not request.env.user.is_merchant \
                and not request.env.user.is_sub_merchant:
            raise UserError("Access Denied")

        if request.env.user.is_sub_merchant:
            BaseController.check_sub_merchant_permission(codes=["1.1"], user=request.env.user)

        product_id = validated.get("product_id")
        domain = [('id', '=', product_id), ("is_redeemly_product", "=", True)]
        product = request.env['product.template'].with_user(1).search(domain)
        if request.env.user.is_service_provider and product.service_provider_id.id != request.env.user.id:
            raise UserError("Product Not Found")
        if request.env.user.is_merchant and not request.env.user.is_sub_merchant and product.id not in request.env.user.invites_ids.product.ids:
            raise UserError("Product Not Found")

        if request.env.user.is_merchant and request.env.user.is_sub_merchant and product.id not in request.env.user.parent_merchant.invites_ids.product.ids:
            raise UserError("Product Not Found")

        return BaseController._create_response(product.name)

    @route("/exposed/get_product_not_invited_to_merchant",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_product_not_invited_to_merchant(self, **kw):
        user = request.env.user
        validated = BaseController.get_validated(
            kw,
            {"merchant_id": "number", "merchant_reference": "string"}
        )
        if not user.is_service_provider:
            raise UserError("Access Denied")

        domain = False
        if validated.get('merchant_id'):
            domain = [('product.service_provider_id', '=', user.id), ('merchant', '=', validated.get('merchant_id'))]
        if validated.get('merchant_reference'):
            domain = [('product.service_provider_id', '=', user.id),
                      ('merchant.reference', '=', validated.get('merchant_reference'))]
        if not domain:
            raise UserError("Ether Merchant ID Or Reference is required")
        merchant_invites = request.env['merchant.package.invites'].sudo().search(domain)
        product_domain = [('service_provider_id', '=', user.id),
                          ("is_redeemly_product", "=", True),
                          ('id', 'not in', merchant_invites.product.ids)
                          ]
        not_invited_products = request.env['product.template'].sudo().search(product_domain)
        data = [item.serialize_for_api_key_value() for item in not_invited_products]
        res = {"data": data}
        return BaseController._create_response(res)

    @route("/exposed/create_product",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_products(self, **kw):
        product_data = BaseController.get_validated(
            kw,
            {
                "name": "string|required",
                "name_ar": "string|required",
                "how_to_use": "string|required",
                "how_to_use_ar": "string|required",
                # "voucher_type_id": "number|required",
                # "voucher_type_fields_value": "dict|required",
                "image": "image",
                'has_serials': "boolean",
                "SKU": "string|required",
                "direct_redeem_link": "string",
                "is_prepaid": "boolean",
                "value": "number",
                "standard_price": "number",
                "expiry_date": "string",
                "expiry_period": "number",
                "use_skarla_portal": "boolean",
                "serials_auto_generated": "boolean",
                "product_attributes": "list",
                "product_specific_attribute": "string",
                "product_currency": "number",
                "product_amount": "number",
                "netdragon_product_description": "string",
                "netdragon_product_category": "number",
                "foodics_discount_type": "string",
                "foodics_discount_amount": "number",
                "foodics_is_percent": "boolean",
                "foodics_business_reference": "string",
                "foodics_max_discount_amount": "number",
                "foodics_include_modifiers": "boolean",
                "foodics_allowed_products": "list",
                "foodics_is_discount_taxable": "boolean",
                "country_id": "number",
                "purchase_currency_id": "number",
                "categ_id": "number",
                "vendor_id": "number",
            },
        )
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        product_data['has_serials'] = True
        if BaseController.is_valid_url(product_data.get("image")):
            product_data["image_url"] = product_data.pop("image")
        else:
            product_data["image_1920"] = product_data.pop("image")
        product_data["service_provider_id"] = request.uid
        product_data["voucher_type_id"] = request.env.ref('redeemly_pin_management.voucher_type_voucher').id
        product_data["detailed_type"] = "service"
        product_data["is_redeemly_product"] = True
        product_data['expiry_date'] = datetime.strptime(product_data["expiry_date"], "%m/%d/%Y") \
            if product_data.get("expiry_date") else None

        if product_data.get('is_prepaid') and not product_data.get('value'):
            raise UserError("Prepaid Cards Should Have A value")
        # if product_data.get('is_prepaid') and not product_data.get('expiry_date'):
        #     raise UserError("Prepaid Cards Should Have A Expiry Date")
        if product_data.get('is_prepaid'):
            product_data["serials_auto_generated"] = True
        if product_data.get('product_attributes'):
            product_data['attribute_definition_ids'] = [(0, 0, {
                'name': item['name'],
                'type': item['type'],
                'required': item['required'],
            }) for item in product_data.get('product_attributes')]
        else:
            product_data['attribute_definition_ids'] = []

        if product_data.get("product_specific_attribute") == 'topup':
            if not product_data.get("product_currency") or not product_data.get("product_amount"):
                raise UserError("currency and amount are required for topup products")

        product_data.pop('product_attributes')

        if not product_data.get('foodics_discount_type'):
            product_data.pop('foodics_discount_type')
        foodics_allowed_products = []
        if product_data.get('foodics_allowed_products'):
            for item in product_data.get('foodics_allowed_products'):
                foodics_allowed_products.append((0, 0, {
                    'product_id': item['product_id'],
                }))
        product_data.pop('foodics_allowed_products')
        product_data['foodics_allowed_products'] = foodics_allowed_products
        product_data['country_id'] = product_data.get("country_id")
        product_data['vendor_id'] = product_data.get("vendor_id")
        product = request.env['product.template'].with_user(1).create(product_data)

        return BaseController._create_response(product.serialize_for_api())

    @route("/exposed/edit_product",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def edit_products(self, **kw):
        product_data = BaseController.get_validated(
            kw,
            {
                "id": "number|required",
                "name": "string|required",
                "name_ar": "string|required",
                "SKU": "string|required",
                "direct_redeem_link": "string",
                "how_to_use": "string|required",
                "how_to_use_ar": "string|required",
                # "voucher_type_id": "number|required",
                # "voucher_type_fields_value": "dict|required",
                "image": "image",
                "value": "number",
                "standard_price": "number",
                "use_skarla_portal": "boolean",
                "expiry_date": "string",
                "expiry_period": "number",
                "product_attributes": "list",
                "enable_stock_history": "boolean",
                "netdragon_product_description": "string",
                "netdragon_product_category": "number",
                "foodics_discount_type": "string",
                "foodics_discount_amount": "number",
                "foodics_is_percent": "boolean",
                "foodics_business_reference": "string",
                "foodics_max_discount_amount": "number",
                "foodics_include_modifiers": "boolean",
                "foodics_allowed_products": "list",
                "foodics_is_discount_taxable": "boolean",
                "country_id": "number",
                "product_currency": "number",
                "purchase_currency_id": "number",
                "categ_id": "number",
                "vendor_id": "number",
            },
        )
        if product_data.get("serials_auto_generated"):
            product_data.pop("serials_auto_generated")
        if BaseController.is_valid_url(product_data.get("image")):
            product_data["image_url"] = product_data.pop("image")
        else:
            product_data["image_1920"] = product_data.pop("image")
        product_data["service_provider_id"] = request.uid
        # product_data["voucher_secret_value"] = json.dumps(product_data.pop('voucher_type_fields_value'))

        if product_data.get('is_prepaid') and not product_data.get('value'):
            raise UserError("Prepaid Cards Should Have A value")
        # if product_data.get('is_prepaid') and not product_data.get('expiry_date'):
        #     raise UserError("Prepaid Cards Should Have Expiry Date")
        product_id = product_data.pop("id")
        product = request.env['product.template'].with_user(1).search([
            ("id", "=", product_id),
            ("service_provider_id", '=', request.uid)
        ])

        if not product:
            raise UserError("Product Not Found")
        if product_data.get('product_attributes'):
            product.attribute_definition_ids.unlink()
            product_data['attribute_definition_ids'] = [(0, 0, {
                'name': item['name'],
                'type': item['type'],
                'required': item['required'],
            }) for item in product_data.get('product_attributes')]
        else:
            product_data['attribute_definition_ids'] = []
        foodics_allowed_products = []
        if product_data.get('foodics_allowed_products'):
            product.foodics_allowed_products.unlink()
            for item in product_data.get('foodics_allowed_products'):
                foodics_allowed_products.append((0, 0, {
                    'product_id': item['product_id'],
                    'skarla_product_id': product_id
                }))
        else:
            product.foodics_allowed_products.unlink()
        product_data.pop('foodics_allowed_products')
        product_data['foodics_allowed_products'] = foodics_allowed_products
        product_data.pop('product_attributes')

        product_data['expiry_date'] = datetime.strptime(product_data["expiry_date"], "%m/%d/%Y") \
            if product_data.get("expiry_date") else None

        if not product_data.get('foodics_discount_type'):
            product_data.pop('foodics_discount_type')

        product.write(product_data)

        return BaseController._create_response(product.serialize_for_api())

    @route("/exposed/archive_product",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def delete_products(self, **kw):
        product_data = BaseController.get_validated(
            kw,
            {
                "id": "number|required",
            },
        )
        product_id = product_data.pop("id")
        product = request.env['product.template'].with_user(1).search([
            ("id", "=", product_id),
            ("service_provider_id", '=', request.uid)
        ])

        if not product:
            raise UserError("Product Not Found")
        product.action_archive()

        return BaseController._create_response({}, 200, "Product Archived")

    @route("/exposed/get_countries",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_countries(self):
        countries = request.env['res.country'].with_user(1).search([])
        res = [{
            'country_id': country.id,
            'country_name': country.name,
            'country_currency_id': country.currency_id.id,
            'country_currency_name': country.currency_id.name,
            'country_currency_unit': country.currency_id.currency_unit_label,
        }
            for country in countries
        ]
        countries_count = len(res)
        res = {'data': res, 'totalCount': countries_count}
        return BaseController._create_response(data=res)

    #####################################################PRODUCT CATEGORY#############################################
    @route("/exposed/get_categories",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_categories(self, **kw):
        if not request.env.user.is_service_provider and not request.env.user.is_sp_finance:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"name": "string", "offset": "int", "limit": "int", "id": "number"},
        )
        service_provider_id = request.uid if request.env.user.is_service_provider else request.env.user.finance_service_provider_id.id
        service_provider_record = request.env['res.users'].sudo().browse(service_provider_id)
        default_categ_id = service_provider_record.default_categ_id.id if service_provider_record.default_categ_id else None
        if default_categ_id:
            domain = [
                ('service_provider_id', '=', service_provider_id),
                ('parent_id', '=', default_categ_id)
            ]
        else:
            domain = [('service_provider_id', '=', service_provider_id), ('parent_id', '!=', False)]

        name = validated.get("name")
        if name:
            domain += [('name', 'ilike', name)]
        category_id = validated.get("id")
        if category_id:
            domain += ["|", ('id', '=', category_id), ('parent_id', '=', category_id)]
        offset = validated.get('offset')
        limit = validated.get("limit")
        categories = request.env['product.category'].with_user(1).search(domain, offset=offset, limit=limit,
                                                                         order="create_date desc")
        totalCount = request.env['product.category'].with_user(1).search_count(domain)
        data = [category.serialize_for_api() for category in categories]

        res = {'data': data, 'totalCount': totalCount}
        return BaseController._create_response(data=res)

    @route("/exposed/create_category",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_category(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        if not request.env.user.default_categ_id:
            raise ValidationError(_("An issue has occurred. Please contact Skarla Technical Support for assistance."))
        validated = BaseController.get_validated(
            kw,
            {
                "name": "string|required",
                "name_ar": "string|required",
                "image": "image|required"
            },
        )
        if BaseController.is_valid_url(validated.get("image")):
            validated["image_url"] = validated.pop("image")
        else:
            validated["image"] = validated.pop("image")


        category = request.env["product.category"].sudo().create(
            {"service_provider_id": request.uid,
             "name": validated["name"],
             "name_ar": validated["name_ar"],
             "image": validated["image"],
             "parent_id": request.env.user.default_categ_id.id})
        return BaseController._create_response(data=category.serialize_for_api())

    @route("/exposed/edit_category",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def edit_category(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        category_data = BaseController.get_validated(
            kw,
            {
                "id": "number|required",
                "name": "string",
                "name_ar": "string",
                "image": "image",
            },
        )
        if BaseController.is_valid_url(category_data.get("image")):
            category_data["image_url"] = category_data.pop("image")
        else:
            category_data["image"] = category_data.pop("image")
        category_id = category_data.pop("id")
        category = request.env['product.category'].sudo().browse(category_id)
        if not category or category.service_provider_id.id != request.uid:
            raise UserError("Category Not Found")

        category.write(category_data)
        return BaseController._create_response(category.serialize_for_api())

    @route("/exposed/archive_category",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           method="POST",
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def archive_category(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        category_data = BaseController.get_validated(
            kw,
            {
                "id": "number|required",
            },
        )
        category_id = category_data.pop("id")
        category = request.env['product.category'].sudo().browse(category_id)

        if not category or category.service_provider_id.id != request.uid:
            raise UserError("Category Not Found")
        category.unlink()
        return BaseController._create_response({}, 200, "Category Deleted successfully")

    @route("/exposed/get_voucher_types",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_voucher_type(self):
        voucher_types = request.env['voucher.type'].with_user(1).search([])
        res = [{
            'id': voucher_type.id,
            'name': voucher_type.name,
            'fields': [{
                "id": field.id,
                "name": field.name,
                "type": field.type,
                "required": field.required
            } for field in voucher_type.voucher_fields]
        }
            for voucher_type in voucher_types
        ]
        return BaseController._create_response(res)

    @route("/exposed/get_vendor_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_vendor_list(self, **kw):
        user = request.env.user
        if not user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {
                "id": "number", "name": "string", "offset": "int", "limit": "int",
            })
        if validated.get('id'):
            sp_vendors = request.env['res.partner'].sudo().browse(validated.get('id'))
            totalCount = 1 if sp_vendors else 0
        else:
            offset = validated.get('offset') or 0
            limit = validated.get('limit') or 20
            domain = [('vendor_user_id', '=', user.id), ('is_vendor', '=', True)]
            if validated.get('name'):
                domain.append(('name', 'ilike', validated.get('name')))

            sp_vendors = request.env['res.partner'].sudo().search(domain, offset=offset, limit=limit)
            totalCount = request.env['res.partner'].sudo().search_count(domain)
        res = [{
            'id': sp_vendor.id,
            'name': sp_vendor.name,
        } for sp_vendor in sp_vendors
        ]
        return BaseController._create_response({"data": res, "totalCount": totalCount}, message='')

    @route("/exposed/create_vendor",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def create_vendor(self, **kw):
        validated_data = BaseController.get_validated(kw, {
            "name": "string|required",

        })
        vendor = request.env['res.partner'].sudo().create([{
            'name': validated_data['name'],
            'is_vendor': True,
            'vendor_user_id': request.uid,
        }])
        return BaseController._create_response(data=vendor.serialize_for_api(), message="Created Successfully")

    @route("/exposed/insert_product_serials",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def insert_product_serials(self, **kw):
        validate_batch = BaseController.get_validated(kw, {
            "batch_sequence": "string|required",
            "batch_file": "string",
            "product_id": "int|required",
            "product_purchase_price": "number|required",
            "batch_currency_id": "number",
            "invoice_ref": "string|required",
            "vendor_id": "number|required",
            "notes": "string",

        })
        batch_id = request.env['batch.serials'].sudo().create([{
            'batch_sequence': validate_batch['batch_sequence'],
            'batch_file': validate_batch['batch_file'],
            'product_id': validate_batch['product_id'],
            'product_purchase_price': validate_batch['product_purchase_price'],
            'batch_currency_id': validate_batch['batch_currency_id'],
            'vendor_id': validate_batch['vendor_id'],
            'invoice_ref': validate_batch['invoice_ref'],
            'notes': validate_batch['notes'],
        }])
        values = batch_id.extract_serials_from_excel()
        request.env.cr.execute("""
                                            insert into public.product_serials(serial_code,
                                                        serial_number,product_id,
                                                        expiry_date, pin_code, value,
                                                        create_date,write_date,
                                                        create_uid, write_uid,
                                                        state,
                                                        serial_code_hash,
                                                        batch_id
                                                        )
                                                        SELECT 
                                                        (rec->>'serial_code')::text,
                                                        (rec->>'serial_number')::text ,
                                                        (rec->>'product_id')::integer,
                                                        (rec->>'expiry_date')::date,
                                                        (rec->>'pin_code')::text,
                                                        (rec->>'value')::integer,
                                                        (rec->>'create_date')::timestamp,
                                                        (rec->>'write_date')::timestamp,
                                                        (rec->>'create_uid')::integer,
                                                        (rec->>'create_uid')::integer,
                                                        (rec->>'state')::text,
                                                        (rec->>'serial_code_hash')::text,
                                                        (rec->>'batch_id')::integer
                                                        FROM 
                                    json_array_elements('%s'::json->'serials' ) rec
                            """ % (json.dumps({'serials': values})))
        return BaseController._create_response(data={}, message="Inserted Successfully")

    @route("/exposed/freeze_batch",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False)
    @BaseController.with_errors
    def freeze_batch(self, **kw):
        validated = BaseController.get_validated(kw,
                                                 {
                                                     "id": "number|required",
                                                 })
        domain = [('create_uid', '=', request.uid), ('state', '=', '1'), ('id', '=', validated['id'])]
        batch_id = request.env['batch.serials'].sudo().search(domain)
        if not batch_id:
            raise UserError("Batch Not Found")
        batch_id.state = '2'
        return BaseController._create_response("Frozen Successfully")

    @route("/exposed/unfreeze_batch",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False)
    @BaseController.with_errors
    def unfreeze_batch(self, **kw):
        validated = BaseController.get_validated(kw,
                                                 {
                                                     "id": "number|required",
                                                 })
        domain = [('create_uid', '=', request.uid), ('state', '=', '2'), ('id', '=', validated['id'])]
        batch_id = request.env['batch.serials'].sudo().search(domain)
        if not batch_id:
            raise UserError("Batch Not Found")
        batch_id.state = '1'
        return BaseController._create_response("UNFrozen Successfully")

    @route("/exposed/batch_serial_list",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False)
    @BaseController.with_errors
    def batch_serial_list(self, **kw):
        user = request.env.user
        if user.is_service_provider or user.is_sp_finance:

            validated = BaseController.get_validated(kw,
                                                     {
                                                         "id": "number|required",
                                                         "create_date": "string",
                                                         "product_name": "string",
                                                         "batch_sequence": "string",
                                                         "invoice_ref": "string",
                                                         "vendor_name": "string",
                                                         "category_name": "string",
                                                         "state": "string",
                                                         "limit": "number",
                                                         "offset": "number",
                                                     })
            limit = validated.get("limit") if validated.get("limit") else 20
            offset = validated.get("offset") if validated.get("offset") else 0
            if user.is_sp_finance:
                domain = [('create_uid', '=', user.finance_service_provider_id.id)]
            else:
                domain = [('create_uid', '=', request.uid)]
            if validated.get('id'):
                domain.append(('id', '=', validated['id']))
            if validated.get('batch_sequence'):
                domain.append(('batch_sequence', 'ilike', validated.get('batch_sequence')))
            if validated.get('create_date'):
                input_date_str = validated.get('create_date')
                input_date = datetime.strptime(input_date_str, "%Y-%m-%d")
                formatted_date = input_date.strftime('%Y-%m-%d')
                print(formatted_date)
                date_domain = [
                    ('create_date', '>=', f"{formatted_date} 00:00:00"),
                    ('create_date', '<=', f"{formatted_date} 23:59:59")
                ]
                domain = date_domain + domain
            if validated.get('product_name'):
                domain.append(('product_id.name', 'ilike', validated.get('product_name')))
            if validated.get('invoice_ref'):
                domain.append(('invoice_ref', 'ilike', validated.get('invoice_ref')))
            if validated.get('category_name'):
                domain.append(('product_id.categ_id.name', 'ilike', validated.get('category_name')))
            if validated.get('vendor_name'):
                domain.append(('vendor_id.name', 'ilike', validated.get('vendor_name')))
            if validated.get('state'):
                state = validated.get('state')
                if state not in ['1', '2']:
                    raise UserError("State must be ('1' for available or '2' for frozen) only")
                domain.append(('state', '=', state))
            batches = request.env['batch.serials'].sudo().search(domain, limit=limit, offset=offset,
                                                                 order='create_date desc')
            totalCount = request.env['batch.serials'].sudo().search_count(domain)
            datas = [item.serialize_for_api() for item in batches]
            res = {'data': datas, 'totalCount': totalCount}
            return BaseController._create_response(data=res)
        else:
            raise AccessDenied()

    @route(
        "/exposed/download_excel_batch_attachment",
        type="http",
        auth="none",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def download_excel_batch_attachment(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"file_hash": "string|required"},
        )
        base_url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('s3.obj_url')
        domain = [('url', '=', base_url + validated['file_hash']), ('res_field', '=', 'batch_file')]
        attach = request.env['ir.attachment'].with_user(SUPERUSER_ID).search(domain, limit=1)
        batch = request.env['batch.serials'].with_user(SUPERUSER_ID).search(
            [('id', '=', attach.res_id)])
        filename = 'Batch Serials - %s.xlsx' % (batch.batch_sequence)
        file = requests.get(attach.url, timeout=5)
        if file:
            content = file.content
            pdfhttpheaders = [('Content-Type', 'application/vnd.ms-excel'), ('Content-Length', len(content)),
                              ('Content-Disposition', content_disposition(filename))
                              ]
            return request.make_response(content, headers=pdfhttpheaders)
        raise AccessDenied()

    @route(
        "/exposed/send_batch_serial_via_email",
        type="json",
        auth="jwt_dashboard",
        save_session=False,
        method=["GET", "POST"],
        cors=config.get("control_panel_url"),
        csrf=False
    )
    @BaseController.with_errors
    def send_batch_serial_via_email(self, **kw):
        validated = BaseController.get_validated(
            kw,
            {"id": "number|required"},
        )
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        batch = request.env['batch.serials'].sudo().search([('id', '=', validated['id'])
                                                            ])
        if batch.serial_ids[0].product_id.service_provider_id.id != request.env.user.id:
            raise AccessDenied()
        batch.send_email()
        return BaseController._create_response(data=[], message="Email Send Successfully")

    @route("/exposed/stock_history",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_stock_history(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"date": "string", "offset": "int", "limit": "int", "product_id": "number"},
        )
        domain = [('product_id.service_provider_id', '=', request.uid)]
        date = validated.get("date")
        product_id = validated.get("product_id")
        offset = validated.get('offset')
        limit = validated.get("limit")
        if date:
            domain += [('history_date', '<=', date)]
        if product_id:
            domain += [('product_id', '=', product_id)]
        history = request.env['serials.stock.history'].with_user(1).search(domain, limit=limit, offset=offset,
                                                                           order="history_date desc")
        history_count = request.env['serials.stock.history'].with_user(1).search_count(domain)
        data = []
        for item in history:
            data.append(item.serialize_for_api())
        res = {'data': data, 'totalCount': history_count}
        return BaseController._create_response(res)

    @route("/exposed/get_available_currencies",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_available_currencies(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()

        res = request.env['res.currency'].with_user(1).search([('active', '=', True)])
        data = [{
            'id': item.id,
            "symbol": item.name
        } for item in res]
        result = {'data': data, 'totalCount': len(data)}
        return BaseController._create_response(result)

    @route("/exposed/get_all_currencies",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_all_currencies(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()

        res = request.env['res.currency'].with_user(1).search(['|', ('active', '=', True), ('active', '=', False)])
        data = [{
            'id': item.id,
            "symbol": item.name
        } for item in res]
        result = {'data': data, 'totalCount': len(data)}
        return BaseController._create_response(result)

    @route("/exposed/get_product_batches",
           type="json",
           auth="jwt_dashboard",
           save_session=False,
           cors=config.get('control_panel_url'))
    @BaseController.with_errors
    def get_product_batches(self, **kw):
        if not request.env.user.is_service_provider:
            raise AccessDenied()
        validated = BaseController.get_validated(
            kw,
            {"offset": "int", "limit": "int", "product_id": "number|required"},
        )

        product_id = validated.get("product_id")
        domain = [('service_provider_id', '=', request.uid),
                  ('id', '=', product_id),
                  ("is_redeemly_product", "=", True)]
        offset = validated.get('offset') if validated.get('offset') else 0
        limit = validated.get("limit") if validated.get('limit') else 4
        product = request.env['product.template'].with_user(1).search(domain)
        if not product:
            raise UserError("Product Not Found")
        batches = product.get_batches_details(limit=limit, offset=offset)
        batches_count = request.env["batch.serials"].sudo().search_count(
            [('serial_ids.product_id', '=', product.id)])
        data = []
        for b in batches:
            data.append(b.serialize_for_api())
        res = {'data': data, 'totalCount': batches_count}
        return BaseController._create_response(res)

    @route("/exposed/get_all_products_stock",
           type="json",
           auth="none",
           save_session=False,
           cors=config.get("control_panel_url"),
           csrf=False
           )
    def get_all_products_stock(self, **kw):
        key = request.httprequest.headers.get('Authorization')
        if not key or key != '0F47583BFFC356F559C8D3BAF7C5B4AAFE00F79AF82EFF5433FC50058FADBE27':
            raise AccessDenied()
        products = request.env['product.template'].sudo().search([('serials_auto_generated', '=', False)])
        if not products:
            return BaseController._create_response([], "ok", 'No Products Available.')
        else:
            data = []
            for product in products:
                vendor_specific_account = request.env['merchant.package.invites'].sudo().search(
                    [('product', '=', product.id), ('merchant.reference', '=', '95fb64a61ac94e0b8ba334f0554f5a05')])
                lastBatch = request.env['batch.serials'].sudo().search([('product_id', '=', product.id)],
                                                                       order="create_date desc", limit=1)

                data.append({
                    'name': product.name,
                    "service provider": product.service_provider_id.name,
                    'available stock': product.product_actual_stock,
                    "price for procurementt@likecard.com": vendor_specific_account.price if vendor_specific_account else '',
                    "last batch purchase price": lastBatch.product_purchase_price if lastBatch
                    else "no batches for this product",
                    "purchase currency": lastBatch.batch_currency_id.name if lastBatch
                    else "no batches for this product",

                })

            res = {'data': data, 'totalCount': len(products)}
        return BaseController._create_response(res)
