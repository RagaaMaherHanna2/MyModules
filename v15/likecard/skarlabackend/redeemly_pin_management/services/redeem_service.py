import datetime

from odoo.exceptions import ValidationError, UserError, AccessDenied
from odoo.http import request
import json
from odoo.addons.redeemly_pin_management.services.code_validation_service import RedeemlyCodeValidationService
from odoo import SUPERUSER_ID, _
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from hashlib import sha256


class RedeemService:
    @staticmethod
    def get_validated_input(kw):
        code = kw.get('code')
        email = kw.get('email')
        reference_user_id = kw.get('user_id')
        if not code:
            raise ValidationError(message="the code field is required")
        if not email:
            raise ValidationError(message="the email field is required")
        if not reference_user_id:
            raise ValidationError(message="the user_id field is required")

        return code, email, reference_user_id

    @staticmethod
    def get_code(code,product_type, reference_user_id, service_provider, pin_code, secret):
        if product_type == 'mask':
            return RedeemService.get_package_code(code, reference_user_id, service_provider)
        if product_type == 'prepaid':
            return RedeemService.get_package_code_prepaid(code, pin_code, reference_user_id, service_provider)
        if product_type == 'serial':
            return RedeemService.get_serial_code(code, service_provider, secret)

    @staticmethod
    def get_package_code(code, reference_user_id, service_provider):
        package_code = request.env['package.codes'].sudo().search(
            [('code', '=', code)])
        if not package_code \
                or not package_code.package.service_provider_id.id == service_provider.id \
                or not package_code.package.state == 'published' \
                or (package_code.reference_user_id and package_code.reference_user_id != reference_user_id) \
                or package_code.status not in ['redeemed', 'pulled']:
            raise ValidationError(message=_("Invalid Code"))
        return package_code

    @staticmethod
    def get_package_code_prepaid(code, pin_code, reference_user_id, service_provider):
        aes_cipher = request.env['aes.cipher'].sudo().create([])
        product_serial = request.env['product.serials'].sudo().search(
            [
                ('pin_code' , '=' , pin_code),
                ('serial_code_hash', '=', sha256(code.encode('utf-8')).hexdigest()),
                ('product_id.service_provider_id', '=', service_provider.id)
            ])
        return product_serial

    @staticmethod
    def get_serial_code(code, service_provider, secret):
        domain = [
                ('serial_code_hash', '=', sha256(code.encode('utf-8')).hexdigest()),
                ('product_id.service_provider_id', '=', service_provider.id)
            ]
        if service_provider.codes_additional_value == 'secret':
            domain = [
                ('serial_code_hash', '=', sha256(code.encode('utf-8')).hexdigest()),
                ('product_id.service_provider_id', '=', service_provider.id),
                ('secret_value', '=', secret)
            ]
        product_serial = request.env['product.serials'].sudo().search(domain)
        return product_serial

    @staticmethod
    def get_redeem_result(code, product_type, deduct_value, language='en'):
        if product_type == 'mask':
            return RedeemService.get_redeem_result_package(code, language)
        if product_type == 'prepaid':
            return RedeemService.get_redeem_result_prepaid(code, deduct_value, language)
        if product_type == 'serial':
            return RedeemService.get_redeem_result_serial(code, language)

    @staticmethod
    def get_redeem_result_serial(code, language):
        product = code.product_id
        redeem_result = {
            'name': product.name if language == 'en' else product.name_ar,
            'product_name': code.product_id.name if language == 'en' else code.product_id.name_ar,
            'pin_code': code.decrypt_serial_code(),
            'image': code.product_id.get_product_image_url(),
            'voucher_type': code.product_id.voucher_type_id.name.upper() if product.voucher_type_id else "VOUCHER",
            'how_to_use': product.how_to_use if product.how_to_use else "",
            'how_to_use_ar': product.how_to_use_ar if product.how_to_use_ar else "",
            "is_redeemed": code.state,
            "sku": code.product_id.SKU,
            'vendor': product.service_provider_id.name.upper() if product.service_provider_id else "SKARLA",
        }
        return redeem_result

    @staticmethod
    def get_redeem_result_package(package_code, language='en'):
        product = package_code.product
        voucher_secret = {}
        for field in json.loads(product.voucher_secret):
            value = field["value"]
            if field["value"] and field['type'] == '2':
                value = int(value)
            if field['type'] == '3':
                value = bool(value)
            voucher_secret[field['name'].upper()] = value
        redeem_result = {
            'name': product.name if language == 'en' else product.name_ar,
            'package_name': package_code.package.package_name if language == 'en' else package_code.package.package_name_ar,
            'pin_code': package_code.name,
            'image': product.get_product_image_url(),
            'voucher_type': product.voucher_type_id.name.upper() if product.voucher_type_id else "VOUCHER",
            "sku": product.SKU,
            'voucher_secret': voucher_secret,
            'how_to_use': product.how_to_use if product.how_to_use else "",
            'how_to_use_ar': product.how_to_use_ar if product.how_to_use_ar else "",
            "is_redeemed": package_code.status == 'redeemed',
            "redeemed_at": datetime.datetime.strftime(package_code.redemption_date,
                                                      DATETIME_FORMAT) if package_code.redemption_date else None,
            'vendor': product.service_provider_id.name.upper() if product.service_provider_id else "REDEEMLY"
        }
        if package_code.get_decrypted_serial_code():
            redeem_result['voucher_secret']['SERIAL'] = package_code.get_decrypted_serial_code()

        return redeem_result

    @staticmethod
    def get_redeem_result_prepaid(package_code,deduct_value, language='en'):
        product = package_code.product_id
        voucher_secret = {}
        for field in json.loads(product.voucher_secret):
            value = field["value"]
            if field["value"] and field['type'] == '2':
                value = int(value)
            if field['type'] == '3':
                value = bool(value)
            voucher_secret[field['name'].upper()] = value
        redeem_result = {
            'name': product.name if language == 'en' else product.name_ar,
            'product_name': package_code.product_id.name if language == 'en' else package_code.product_id.name_ar,
            'pin_code': package_code.decrypt_serial_code(),
            'image': package_code.product_id.get_product_image_url(),
            'voucher_type': package_code.product_id.voucher_type_id.name.upper() if product.voucher_type_id else "VOUCHER",
            'voucher_secret': voucher_secret,
            'how_to_use': product.how_to_use if product.how_to_use else "",
            'how_to_use_ar': product.how_to_use_ar if product.how_to_use_ar else "",
            "is_redeemed": package_code.state,
            "sku": product.SKU,
            'vendor': product.service_provider_id.name.upper() if product.service_provider_id else "SKARLA",
            'Original Value' : package_code.original_value,
            'value': deduct_value,
            'remaining_value': package_code.value,
        }
        return redeem_result

    @staticmethod
    def validate_code(code):
        validation_service = RedeemlyCodeValidationService(code)
        for code_type in ["alpha", "numeric", "alphanumeric"]:
            try:
                validated = validation_service.validate(code_type)
                if validated:
                    return validated
            except KeyError:
                pass
        raise ValidationError(_("Invalid Code"))

    @staticmethod
    def redeem(code, product_type):
        if product_type == 'mask':
            if code.status == 'redeemed':
                return
            if code.get_decrypted_serial_code():
                serial = code.serial_id
                serial.state = '5'
            code.redeem()
        if product_type == 'prepaid':
            if code.state == '5':
                return
            elif code.value == 0:
                code.state = '5'
        if product_type == 'serial':
            if code.state == '5':
                return
            else:
                code.state = '5'

    @staticmethod
    def get_message(language, state):
        if state == '5':
            return _("Code Already Redeemed")
        else:
            return _("Code Redeemed Successfully")
