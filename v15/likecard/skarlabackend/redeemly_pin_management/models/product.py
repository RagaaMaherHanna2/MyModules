# -*- coding: utf-8 -*-
from odoo.addons.redeemly_pin_management.services.babel_voucher_service import BabelVoucherService
from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError
import logging
import requests
import base64
from odoo.tools import config
import uuid
import random
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ProductTemplateConfigurator(models.Model):
    _inherit = 'product.template'

    is_redeemly_product = fields.Boolean(string='Redeemly Product')
    how_to_use = fields.Char(string='How to use URL')
    how_to_use_ar = fields.Char(string='Arabic How to use URL')
    name_ar = fields.Char(string='Arabic Name')
    service_provider_id = fields.Many2one('res.users', string='Service Provider',
                                          domain=[('is_service_provider', '=', True)], index=True)

    product_serials_stock = fields.Integer(string='Product Serials Stock', default=0,
                                           compute='_compute_product_serial_stock')
    product_total_stock = fields.Integer(string='Product Total Stock', default=0,
                                         compute='_compute_product_serial_stock')

    product_actual_stock = fields.Integer(string='Product Actual Stock', default=0,
                                          compute='_compute_product_serial_stock')

    product_redeemed_stock = fields.Integer(string='Product Redeemed Stock', default=0,
                                            compute='_compute_product_serial_stock')

    product_expired_stock = fields.Integer(string='Product Expired Stock', default=0,
                                           compute='_compute_product_serial_stock')
    frozen_serial_count = fields.Integer(string='Frozen Stock', default=0, compute='compute_frozen_serials_count')

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type')

    voucher_secret = fields.Char("Voucher Secret Data", default='[]', compute="_compute_voucher_secret")
    voucher_secret_value = fields.Char("Voucher Type Fields Values", default='{}')

    image_url = fields.Char(string='Image URL',
                            help="You Can Paste an Image URL")

    has_serials = fields.Boolean("Has Product Serials", default=False)
    SKU = fields.Char(string='SKU')
    direct_redeem_link = fields.Char(string='Direct Redeem Link')

    expiry_date = fields.Date(string='Expiry Date')
    expiry_period = fields.Integer(string='Expiry Period In Date')
    use_skarla_portal = fields.Boolean(string='Use Skarla Redemption Portal', default=False)
    serials_auto_generated = fields.Boolean(string='Serials Auto Generated', default=False)
    attribute_definition_ids = fields.One2many('product.attribute.definition', inverse_name='product_id')

    # Prepaid Card Product
    is_prepaid = fields.Boolean(string="Is Prepaid Card")
    value = fields.Integer("Value")
    enable_stock_history = fields.Boolean('Enable Stock History', default=False)
    product_specific_attribute = fields.Selection(selection=[
        ('topup', 'Top-up')
    ], default=False, string="product_specific_attribute")
    product_amount = fields.Float(string="Product Amount")
    netdragon_product_description = fields.Char(string="Net Dragon Product Description")
    netdragon_product_category = fields.Many2one('netdragon.product.category')

    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id',
                                help="Default taxes used when selling the product.", string='Customer Taxes',
                                domain=[('type_tax_use', '=', 'sale')],
                                default=False)
    foodics_discount_type = fields.Selection(selection=[('1', 'Order Level'),
                                                        ('2', 'Product Level')
                                                        ])
    foodics_discount_amount = fields.Float(string='Discount Amount')
    foodics_is_percent = fields.Boolean(string='Is Percentage')
    foodics_business_reference = fields.Char(string='Business Reference')
    foodics_max_discount_amount = fields.Float(string='Max Discount Amount')
    foodics_include_modifiers = fields.Boolean(string='Discount Include Modifiers')
    foodics_allowed_products = fields.One2many('foodics.allowed.products', inverse_name='skarla_product_id')
    foodics_is_discount_taxable = fields.Boolean(string='Is Discount Taxable')

    country_id = fields.Many2one('res.country', string='Country')
    product_currency = fields.Many2one('res.currency')  # used for topup products

    purchase_currency_id = fields.Many2one('res.currency')
    purchase_cost = fields.Monetary(compute='get_cost_in_another_currency', currency_field='purchase_currency_id')
    vendor_id = fields.Many2one('res.partner', string='Vendor ID')

    @api.depends('standard_price', 'purchase_currency_id')
    def get_cost_in_another_currency(self):
        for rec in self:
            rec.purchase_cost = rec.purchase_currency_id.compute(rec.standard_price,
                                                                 rec.service_provider_id.sp_currency
                                                                 ) \
                if rec.standard_price and rec.purchase_currency_id else rec.standard_price

    _sql_constraints = [
        ('unique_sku', 'UNIQUE(service_provider_id, "SKU"', 'Multiple Products With Same SKU.'),
    ]

    def action_archive(self):
        self.ensure_one()
        if self.is_redeemly_product:
            if not self.service_provider_id.archived_products_categ_id:
                raise UserError(
                    "Archived Products Category is not set for the service provider. Please set it before archiving the product.")
            sql = """
            select distinct batch_id from public.product_serials where product_id = %s
            """ % (self.id)
            self._cr.execute(sql)
            res = self._cr.fetchall()
            batches = self.env['batch.serials'].search([('id', 'in', res)])
            for item in batches:
                item.action_freeze()
            invitations = self.env['merchant.package.invites'].search([('product', '=', self.id)])
            for invitation in invitations:
                invitation.enabled = False
            self.categ_id = self.service_provider_id.archived_products_categ_id.id
        super(ProductTemplateConfigurator, self).action_archive()

    @api.constrains('SKU')
    def check_sku_unique(self):
        for rec in self:
            count = self.search_count([('service_provider_id', '=', rec.service_provider_id.id),
                                       ('SKU', '=', rec.SKU),
                                       ('id', '!=', rec.id)
                                       ])
            if count > 0:
                raise UserError("Duplicate SKU Found")

    def compute_frozen_serials_count(self):
        for rec in self:
            rec.frozen_serial_count = self.env['product.serials'].search_count(
                [('product_id', '=', rec.id), ('state', '=', '1'),
                 ('batch_id.state', '=', '2')
                 ])

    def get_batches_details(self, limit=4, offset=0):
        return self.env["batch.serials"].sudo().search(
            [('serial_ids.product_id', '=', self.id)], limit=limit, offset=offset, order='id desc')

    def get_product_serials_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('state', '=', '1'), ('product_id', '=', self.id)])

    def get_product_total_stock(self):
        return self.env["product.serials"].sudo().search_count([('product_id', '=', self.id)])

    def get_product_redeemed_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('state', 'in', ['3', '5']), ('product_id', '=', self.id)])

    def get_product_expired_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('state', '=', '4'), ('product_id', '=', self.id)])

    def get_product_serials_redeemed(self):
        return self.env["product.serials"].search_count(
            [('state', 'in', ['3', '5']), ('product_id', '=', self.id)])

    def get_product_serials_expired(self):
        return self.env["product.serials"].search_count(
            [('state', '=', '4'), ('product_id', '=', self.id)])

    def get_product_actual_stock(self):
        return self.env["product.serials"].search_count(
            [('state', '=', '1'), ('product_id', '=', self.id),
             ('batch_id.state', '=', '1')
             ])

    def _compute_product_serial_stock(self):
        for rec in self:
            rec.product_serials_stock = rec.get_product_serials_stock() if not rec.serials_auto_generated else 0
            rec.product_total_stock = rec.get_product_total_stock() if not rec.serials_auto_generated else 0
            rec.product_redeemed_stock = rec.get_product_redeemed_stock()
            rec.product_expired_stock = rec.get_product_expired_stock() if not rec.serials_auto_generated else 0
            rec.product_actual_stock = rec.get_product_actual_stock() if not rec.serials_auto_generated else 0

    def get_product_image_base64(self):
        if self.image_1920:
            return str(self.image_1920, 'utf-8')
        if self.image_url:
            return str(base64.b64encode(requests.get(self.image_url).content))
        return ""

    def get_product_image_url(self):
        # if self.image_url:
        #     return self.image_url
        attachment = self.env['ir.attachment'].search(
            [("res_model", "=", "product.template"), ('res_id', '=', self.id), ('res_field', '=', 'image_1920')])
        if attachment:
            if attachment[0].url:
                self.sudo().write({
                    "image_url": attachment[0].url
                })
                return attachment[0].url
            else:
                return config.get('base_url') + attachment.image_src
        return ""

    def get_product_invitation(self):
        return [item.serialize_for_api() for item in
                self.env['merchant.package.invites'].search([('product', '=', self.id)])]

    def get_product_packages(self):
        grouped = self.env['package.codes'].with_user(1).read_group(
            [('product', '=', self.id)],
            ["package"], ['package'])

        packages = [
            {
                "package": self.env['package'].browse(p["package"][0]),
                "package_count": p['package_count']
            }
            for p in grouped
        ]
        packages = [
            {
                "package_name": p['package'].package_name,
                "package_name_ar": p['package'].package_name_ar if p['package'].package_name_ar else "",
                "reference": p['package'].name,
                "quantity": p['package_count']
            }
            for p in packages
        ]

        return packages

    def pull_serials(self, merchant, order_id, customer_mobile_number=False,
                     mobile_country_code=False, business_reference=False, quantity=1,
                     email_id=False, now=datetime.now(), distributor=False,
                     country_of_generation_parameters=False):
        if self.serials_auto_generated or self.is_prepaid:
            if self.expiry_date and datetime.combine(self.expiry_date, datetime.min.time()) < datetime.now():
                return []
            res = self.set_serials(merchant_id=merchant, order_id=order_id,
                                   customer_mobile_number=customer_mobile_number,
                                   mobile_country_code=mobile_country_code, business_reference=business_reference,
                                   quantity=quantity, email_id=email_id, now=now, distributor=distributor,
                                   country_of_generation_parameters=country_of_generation_parameters)
            pulled_serials = [[item.serial_number,
                               item.serial_code,
                               item.product_id.id,
                               item.product_id.name,
                               item.product_id.SKU,
                               item.expiry_date,
                               item.value,
                               item.pin_code,
                               ] for item in res]
        else:
            self._cr.execute("""
                WITH pulled_serials AS (
                    SELECT serials.id ,
                    pt.id as product_template_id,
                    pt.name as product_template_name,
                    pt."SKU" as sku_name
                    FROM product_serials serials
                    JOIN batch_serials bch on bch.id = serials.batch_id
                    JOIN product_template pt on pt.id = serials.product_id 
                    and serials.state = '1'
                    and bch.state = '1'
                    and pt.id = %s
                    and (current_date < serials.expiry_date or serials.expiry_date is null)
                    ORDER BY RANDOM()
                    LIMIT %s
                    FOR UPDATE
                )
                UPDATE product_serials as serials
                SET state = '3',
                    pull_date = %s,
                    pulled_by = %s,
                    order_id = %s
                FROM pulled_serials
                WHERE pulled_serials.id = serials.id
                RETURNING serials.serial_number , 
                          serials.serial_code,
                           pulled_serials.product_template_id, 
                           pulled_serials.product_template_name ,
                           pulled_serials.sku_name,
                           serials.expiry_date,
                           serials.value,
                           serials.pin_code
            """, [self.id, quantity, now, merchant.id, order_id.id])

            pulled_serials = set(self._cr.fetchall())
        return pulled_serials

    def set_serials(self, merchant_id, order_id, customer_mobile_number=False,
                    mobile_country_code=False, business_reference=False,
                    quantity=1, email_id="", now=datetime.now(), distributor=False,
                    country_of_generation_parameters=False):
        values = []
        expiry_date = None
        if self.expiry_date:
            expiry_date = self.expiry_date
        elif self.expiry_period > 0:
            expiry_date = datetime.now().date() + timedelta(days=self.expiry_period)

        def generate_serial_code_16():
            ### generate serial code random from 16 characters , each 4 characters seperated by - ###
            id = uuid.uuid4()
            random_string = str(id.int)[:16]

            # Split the string into 4-character parts
            parts = [random_string[i:i + 4] for i in range(0, len(random_string), 4)]

            # Join the parts with a "-"
            result = "".join(parts)
            view_result = "".join(parts)
            ###   where result variable represent serial_code ###
            return result

        secrets_to_send = []
        for i in range(quantity):
            code = generate_serial_code_16()
            if self.service_provider_id.codes_additional_value == 'secret':
                sec = BabelVoucherService.generate_secret_key()
                secrets_to_send.append({"code": code, "secret": sec})
            else:
                sec = False
            values.append({
                "serial_code": code,
                "serial_number": str(uuid.uuid4()),
                "product_id": self.id,
                "pin_code": random.randint(1000, 9999) if self.is_prepaid else False,
                "value": self.value if self.is_prepaid else 0,
                "original_value": self.value,
                "expiry_date": expiry_date,
                "email_id": email_id if self.is_prepaid else False,
                "state": "3",
                "pulled_by": merchant_id.id,
                "pull_date": now,
                'order_id': order_id.id,
                'secret_value': sec,
                'customer_mobile_number': customer_mobile_number,
                'mobile_country_code': mobile_country_code,
                'business_reference': business_reference,
                'distributor': distributor,
                'country_of_generation_parameters': country_of_generation_parameters
            })
        if len(secrets_to_send) > 0:
            BabelVoucherService.send_generated_codes(secrets_to_send, self.SKU, distributor, country_of_generation_parameters)
        _logger.info('%s values', values)
        sp = self.env['product.serials'].with_user(1).create(
            values
        )
        _logger.info('%s product serial', sp)

        return sp

    @api.model_create_multi
    def create(self, vals):
        res = super(ProductTemplateConfigurator, self).create(vals_list=vals)
        for rec in res:
            if rec.detailed_type != 'service' and rec.is_redeemly_product:
                raise UserError("You can only use service products for redeemly")
        return res

    def write(self, vals):
        super(ProductTemplateConfigurator, self).write(vals)
        attachments = self.env['ir.attachment'].search(
            [("res_model", "=", "product.template"), ('res_field', '=', 'image_1920')])
        for rec in self:
            if rec.detailed_type != 'service' and rec.is_redeemly_product:
                raise UserError("You can only use service products for redeemly")

            rec_attachment = attachments.filtered(lambda att: att.res_id == rec.id)
            if not vals.get("image_url") and rec_attachment:
                super(ProductTemplateConfigurator, self).write({
                    "image_url": rec_attachment.url
                })

    @api.onchange('voucher_type_id', "voucher_secret_value")
    def _compute_voucher_secret(self):
        data = []
        values = json.loads(self.voucher_secret_value)
        for field in self.voucher_type_id.voucher_fields:
            data.append({
                "id": field.id,
                "name": field.name,
                "type": field.type,
                "required": field.required,
                "value": values[str(field.id)] if str(field.id) in values.keys() else "",
            })

        self.voucher_secret = json.dumps(data)

    def update_voucher_secret_value(self, new_value):
        self.voucher_secret_value = new_value

    def open_fields_value_populater(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            'redeemly_pin_management.voucher_type_fields_value_populate')

        json_value = self.voucher_secret

        view_id = self.env.ref(
            'redeemly_pin_management.voucher_type_fields_value_edit_tree').id
        action.update({
            'views': [[False, 'form']],
            'view_id': view_id,
            'context': "{'default_json_value': '%s'}" % json_value,
        })
        return action

    def serialize_for_api_profile(self):
        return [{
            "id": item.id,
            'name': item.name,
            'type': item.type,
            'required': item.required
        } for item in self.attribute_definition_ids],

    def serialize_for_api_key_value(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'purchase_cost': self.purchase_cost,
        }

    def serialize_for_api(self, id=False):
        return {
            'id': self.id,
            'name': self.name,
            'name_ar': self.name_ar if self.name_ar else "",
            "categ_name": self.categ_id.name,
            'image': self.get_product_image_url(),
            "how_to_use": self.how_to_use if self.how_to_use else "",
            "how_to_use_ar": self.how_to_use_ar if self.how_to_use_ar else "",
            # "has_serials": self.has_serials,
            "product_total_stock": self.product_total_stock,
            "product_serials_stock": self.product_serials_stock,
            "SKU": self.SKU,
            'is_prepaid': self.is_prepaid,
            'serials_auto_generated': self.serials_auto_generated,
            "value": self.value,
            "expiry_date": datetime.strftime(self.expiry_date, DATETIME_FORMAT) if self.expiry_date else None,
            "expiry_period": self.expiry_period,
            "direct_redeem_link": self.direct_redeem_link,
            "standard_price": round(self.standard_price, 2),
            "use_skarla_portal": self.use_skarla_portal,
            'inventory_status': {
                'available_count': self.product_actual_stock,
                'redeemed_count': self.product_redeemed_stock,
                'expired_count': self.product_expired_stock,
                'frozen_serial_count': self.frozen_serial_count
            },
            'product_attributes': [{
                'id': item.id,
                'name': item.name,
                'type': item.type,
                'required': item.required
            } for item in self.attribute_definition_ids] if id else False,
            # "batches": [item.serialize_for_api() for item in self.get_batches_details()] if id else [],
            "invited_merchant": self.get_product_invitation() if id else [],
            'enable_stock_history': self.enable_stock_history,
            "product_specific_attribute": self.product_specific_attribute,
            "netdragon_product_category": {
                'id': self.netdragon_product_category.id,
                'name': self.netdragon_product_category.name
            } if self.netdragon_product_category else {},

            "product_amount": self.product_amount,
            'foodics_discount_type': self.foodics_discount_type,
            'foodics_discount_amount': self.foodics_discount_amount,
            'foodics_is_percent': self.foodics_is_percent,
            'foodics_business_reference': self.foodics_business_reference,
            'foodics_max_discount_amount': self.foodics_max_discount_amount,
            'foodics_include_modifiers': self.foodics_include_modifiers,
            'foodics_allowed_products': [item.serialize_for_api() for item in
                                         self.foodics_allowed_products] if self.foodics_allowed_products else [],
            'foodics_is_discount_taxable': self.foodics_is_discount_taxable,
            'netdragon_product_description': self.netdragon_product_description,
            'country_id': self.country_id.id,
            "product_currency": {
                "id": self.product_currency.id,
                "symbol": self.product_currency.name,
            },
            "purchase_currency_id": {
                "id": self.purchase_currency_id.id,
                "symbol": self.purchase_currency_id.name,
            },
            "purchase_cost": self.purchase_cost,
            "categ_id": self.categ_id.id,
            "parent_categ_id": self.categ_id.parent_id.id,
            "parent_categ_name": self.categ_id.parent_id.name,
            "vendor_id": self.vendor_id.id or "",
            "vendor_name": self.vendor_id.name or "",
        }


class ProductProductInherited(models.Model):
    _inherit = 'product.product'

    service_provider_id = fields.Many2one('res.users', related='product_tmpl_id.service_provider_id')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    name_ar = fields.Char('Arabic Name')
    service_provider_id = fields.Many2one('res.users', 'Service Provider')
    image = fields.Image("Image")

    image_url = fields.Char(string='Image URL',
                            help="You Can Paste an Image URL")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_linked_products(self):
        categ_products = self.env['product.template'].search(
            ['|', ('categ_id', '=', self.id), ('categ_id.parent_id', '=', self.id)])
        if categ_products:
            raise UserError('You cannot delete category related to an active products!')

    def get_category_image_url(self):
        if self.image_url:
            return self.image_url
        attachment = self.env['ir.attachment'].search([('res_id', '=', self.id), ('res_field', '=', 'image')])
        if attachment:
            if attachment[0].url:
                return attachment[0].url
            else:
                _logger.info('attachment:%s', attachment.image_src)
                return "https://redeemly-odoo.s3.me-south-1.amazonaws.com/redeemly-odoo/odoo/e3e4a4ad6c498543e8157ca20dee57297c441643"
        return ""

    def serialize_for_api(self, id=False):
        return {
            'id': id or self.id,
            'name': self.name,
            'name_ar': self.name_ar,
            'parent_id': self.parent_id.id if self.parent_id else "",
            'image': self.get_category_image_url(),
            'product_count': self.product_count,
        }


class VoucherType(models.Model):
    _name = 'voucher.type'
    _description = 'Voucher Code Type'

    name = fields.Char("Name", help='Product Type Name')

    products = fields.One2many(
        comodel_name='product.template', inverse_name="voucher_type_id")

    voucher_fields = fields.One2many(
        comodel_name='voucher.type.field', inverse_name="voucher_type_id")


class VoucherTypeFields(models.Model):
    _name = 'voucher.type.field'
    _description = 'Define a field for a voucher type'

    name = fields.Char(
        string='Name', help='The name of the voucher type field')
    type = fields.Selection([('1', 'Text'), ('2', 'Number'), ('3', 'Boolean')],
                            string='Type', help='The field data type')
    required = fields.Boolean(
        string='Required', help='If Unchecked , this field will not be required')

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type')


class ProductAttributeDefinition(models.Model):
    _name = 'product.attribute.definition'
    _description = 'Product Attributes Definition'

    name = fields.Char(
        string='Name', help='The name of the voucher type field')
    type = fields.Selection([('text', 'Text'), ('number', 'Number'), ('boolean', 'Boolean')],
                            string='Type', help='The field data type')
    required = fields.Boolean(
        string='Required', help='If Unchecked , this field will not be required')

    product_id = fields.Many2one('product.template')


class ProductAttributeValues(models.Model):
    _name = 'product.attribute.values'
    _description = 'Product Attributes Definition'

    name = fields.Char(
        string='Name', help='The name of the voucher type field')
    type = fields.Selection([('text', 'Text'), ('number', 'Number'), ('boolean', 'Boolean')],
                            string='Type', help='The field data type')
    required = fields.Boolean(
        string='Required', help='If Unchecked , this field will not be required')

    product_id = fields.Many2one('product.template')
    value = fields.Char(string="Value")
    history_id = fields.Many2one('redeem.history.prepaid')

    def serialize_for_api(self):
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "product_id": self.product_id.id,
            "product_name": self.product_id.name,
            "value": self.value
        }


class FoodicsAllowedProduct(models.Model):
    _name = 'foodics.allowed.products'
    _description = 'Foodics Allowed Products'

    product_id = fields.Char(string='Product Id')
    skarla_product_id = fields.Many2one('product.template')

    def serialize_for_api(self):
        return {
            'product_id': self.product_id,
            'skarla_product_id': self.skarla_product_id.id
        }
