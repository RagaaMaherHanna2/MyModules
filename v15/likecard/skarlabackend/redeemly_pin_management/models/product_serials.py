import base64
import uuid
import datetime
from odoo import models, fields, api, _
from hashlib import sha256
import xlrd
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools import config
import logging

_logger = logging.getLogger(__name__)


class BatchSerials(models.Model):
    _name = 'batch.serials'
    _rec_name = 'batch_sequence'

    batch_sequence = fields.Char(string='Batch sequence')
    serial_ids = fields.One2many('product.serials', string='serials', inverse_name='batch_id')
    state = fields.Selection(selection=[
        ('1', 'available'),
        ('2', 'frozen'),
    ], string='state', default='1')
    batch_file = fields.Binary(string='Batch File')

    product_id = fields.Many2one('product.template', string='Product')
    product_purchase_price = fields.Float(string='Product Purchase Price')
    batch_currency_id = fields.Many2one('res.currency', string='Batch Price')
    vendor_name = fields.Char(string='Vendor Name')
    vendor_id = fields.Many2one('res.partner', string='Vendor ID')
    invoice_ref = fields.Char(string='Invoice Ref')
    notes = fields.Char(string='Notes')

    def get_product_redeemed_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('state', 'in', ['3', '5']), ('batch_id', '=', self.id)])

    def get_product_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('batch_id', '=', self.id)])

    def get_product_avilable_stock(self):
        return self.env["product.serials"].sudo().search_count(
            [('batch_id', '=', self.id), ('state', '=', '1')])

    def get_public_url(self):
        self.ensure_one()
        url = self.get_file_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param('s3.obj_url')
        return url.replace(base_url, "/exposed/download_excel_batch_attachment?file_hash=") if url else False

    def get_file_url(self):
        attachment = self.env['ir.attachment'].search(
            [("res_model", "=", self._name), ('res_id', '=', self.id), ('res_field', '=', 'batch_file')])
        return attachment.url if attachment else False

    def send_email(self):
        self.ensure_one()
        template = self.env.ref("redeemly_pin_management.batch_serial_email_template")
        email_values = {
            'email_from': 'noreply@skarla.com'
        }
        logo_url = self.env['res.partner'].sudo().search([('id', '=', self.env.company.partner_id.id)]).partner_logo_url
        context = {'skarla_logo_url': logo_url, 'server_base_url': config.get('server_base_url')}
        template.with_context(context).send_mail(self.id, email_values=email_values)

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'id': self.id,
            'batch_sequence': self.batch_sequence,
            'state': self.state,
            'batch_file': self.get_public_url(),
            'batch_count': self.get_product_stock(),
            'product_id': self.serial_ids[0].product_id.id if self.serial_ids else False,
            'product_name': self.product_id.name,
            'product_purchase_price': self.product_purchase_price,
            'batch_currency_id': self.batch_currency_id.id if self.batch_currency_id else False,
            'batch_currency_name': self.batch_currency_id.name if self.batch_currency_id else '',
            'invoice_ref': self.invoice_ref if self.invoice_ref else '',
            'vendor_id': self.vendor_id.id if self.vendor_id else False,
            'vendor_name': self.vendor_id.name if self.vendor_id else '',
            'notes': self.notes if self.notes else '',
            'available_count': self.get_product_avilable_stock(),
            'redeemed_count': self.get_product_redeemed_stock(),
            'create_date': datetime.datetime.strftime(self.create_date, DATETIME_FORMAT),
            'category_id': self.serial_ids[0].product_id.categ_id.id if self.product_id.categ_id else False,
            'category_name': self.product_id.categ_id.name if self.product_id.categ_id else '',

        }

    def action_freeze(self):
        for rec in self:
            rec.state = '2'

    def extract_serials_from_excel(self):
        self.ensure_one()
        values = []
        products = []
        wb = xlrd.open_workbook(file_contents=base64.b64decode(self.batch_file))
        sheet = wb.sheet_by_index(0)
        aes_cipher = self.env['aes.cipher'].create([])
        row_num = 0
        for row in range(sheet.nrows):
            row_num = row_num + 1
            if row >= 1:
                row_vals = sheet.row_values(row)
                if len(row_vals) < 4:
                    raise UserError("missing serial code or sku or product id in row %s" % (row_num))
                serial_code = row_vals[1]
                if isinstance(serial_code, int) or isinstance(serial_code, float):
                    serial_code = str(int(serial_code))
                sku = row_vals[2]
                product_id = int(row_vals[3])
                if not serial_code or not sku or not product_id:
                    raise UserError("missing serial code or sku or product id in row %s" % (row_num))
                if isinstance(sku, int) or isinstance(sku, float):
                    sku = str(int(sku))
                if len(row_vals) > 4 and row_vals[4]:
                    try:
                        expiry_date = datetime.datetime.strftime(datetime.datetime.fromordinal(
                            datetime.datetime(1900, 1, 1).toordinal() + int(row_vals[4]) - 2), DATETIME_FORMAT)
                    except Exception as e:
                        raise UserError("Invalid Expiry Date ")
                else:
                    expiry_date = None
                if len(row_vals) > 5:
                    serial_number = row_vals[5]
                else:
                    serial_number = False
                if isinstance(serial_number, int) or isinstance(serial_number, float):
                    print('sss', serial_number)
                    serial_number = str(int(serial_number))
                if product_id not in products:
                    products.append(product_id)
                if len(products) > 1:
                    raise UserError("You Can Upload Only One Product Per Batch")
                product_exists = self.env['product.template'].with_user(1).search(
                    [("id", '=', product_id),
                     ('SKU', '=', sku),
                     ('service_provider_id', '=', self.env.user.id)])
                if not product_exists:
                    raise UserError(f"Product {product_id} With SKU {sku} Not Found For Serial {serial_code}")
                if product_exists.serials_auto_generated:
                    raise UserError(f"Product {product_id} With SKU {sku} Is Defined To Be Auto Generated  By Platform")
                values.append({
                    'product_id': product_id,
                    'serial_code': str(aes_cipher.encrypt(serial_code), 'utf8'),
                    'expiry_date': expiry_date,
                    'serial_number': serial_number if serial_number else str(uuid.uuid4()),
                    'create_date': datetime.datetime.strftime(datetime.datetime.utcnow(), DATETIME_FORMAT),
                    'write_date': datetime.datetime.strftime(datetime.datetime.utcnow(), DATETIME_FORMAT),
                    'create_uid': self.env.user.id,
                    'write_uid': self.env.user.id,
                    'state': '1',
                    'serial_code_hash': sha256(serial_code.encode('utf-8')).hexdigest(),
                    'batch_id': self.id
                })
        if len(values) == 0:
            raise UserError("Empty Batch File")
        return values

    # def fill_old_batches_with_product_id(self):
    #     batches_without_product_id = self.search([('product_id', '=', False)])
    #     for batch in batches_without_product_id:
    #         batch.product_id = batch.serial_ids[0].product_id if batch.serial_ids else False

    # def fill_old_batches_with_vendor_id(self):
    #     batches_without_vendor_id = self.search([
    #         ('vendor_id', '=', False),
    #         ('vendor_name', '!=', False)
    #     ])
    #
    #     Vendor = self.env['res.partner']
    #
    #     for batch in batches_without_vendor_id:
    #         service_provider_id = batch.product_id.service_provider_id.id
    #         vendor_name = batch.vendor_name
    #         # Search for an existing vendor with the same name and vendor_user_id (sp.id)
    #         existing_vendor = Vendor.sudo().search([
    #             ('name', '=', vendor_name),
    #             ('vendor_user_id', '=', service_provider_id)
    #         ], limit=1)
    #
    #         if not existing_vendor:
    #             new_vendor = Vendor.sudo().create({
    #                 'name': vendor_name,
    #                 'is_vendor': True,
    #                 'vendor_user_id': service_provider_id
    #             })
    #             batch.vendor_id = new_vendor
    #         else:
    #             batch.vendor_id = existing_vendor


class ProductSerials(models.Model):
    _name = 'product.serials'
    _rec_name = "serial_number"

    serial_number = fields.Char(string='Serial Number', unique=True)
    serial_code = fields.Char(string='Serial Code', required=True, unique=True)
    serial_code_hash = fields.Char(string='Serial Code Hash')

    product_id = fields.Many2one('product.template', string='Product', required=True)
    state = fields.Selection([
        ('1', 'Available'),
        ('2', 'Reserved'),
        ('3', 'Unknown'),
        ('5', 'Redeemed'),
        ('4', 'Expired')
    ], index=True, default="1")
    pull_date = fields.Datetime('Pull Date')
    pulled_by = fields.Many2one("res.users", domain=[('is_merchant', '=', True)], index=True)
    expiry_date = fields.Date(string='Expiration Date')
    check_count = fields.Integer(string='Check Count')
    order_id = fields.Many2one('sale.order')
    last_check_time = fields.Datetime(string='Check Date')
    generation_request_id = fields.Many2one('package.generation.request', string='Generation Request')

    # if product is prepaid card product
    pin_code = fields.Char(string='Pin Code')
    original_value = fields.Integer(string="Original Value")
    value = fields.Integer(string='Value')

    # redeemed by customer or email_id
    email_id = fields.Char(string='Email Id')
    user_id = fields.Char(string='User Id')
    transaction_id = fields.Char(string='Transaction Id')
    redeem_history_prepaid_ids = fields.One2many('redeem.history.prepaid', 'product_serial')
    batch_id = fields.Many2one('batch.serials')
    secret_value = fields.Char(string='Secret Value')
    customer_mobile_number = fields.Char(string='Customer Mobile Number')
    mobile_country_code = fields.Char(string='Mobile Country Code')
    business_reference = fields.Char(string='Business Reference')
    _sql_constraints = [('unique_serial_unique', 'unique(serial_code_hash)', "Duplicated Serials Not Allowed")]
    distributor = fields.Char(string='Distributor')
    country_of_generation_parameters = fields.Char(string='Country of the generation parameters')

    @api.constrains('serial_code_hash')
    def check_hash_unique(self):
        for rec in self:
            count = self.search_count([('serial_code_hash', '=', rec.serial_code_hash), ('id', '!=', rec.id)])
            if count > 0:
                raise UserError("Duplicate Serial Found")

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['serial_code_hash'] = sha256(val['serial_code'].encode('utf-8')).hexdigest()
        vals_list = self.encrypt_serial_codes(vals_list=vals_list)
        vals_list = self.set_default_serial_numbers(vals_list)
        return super(ProductSerials, self).create(vals_list=vals_list)

    @staticmethod
    def set_default_serial_numbers(vals_list):
        for val in vals_list:
            if not val.get("serial_number"):
                val["serial_number"] = str(uuid.uuid4())
        return vals_list

    def encrypt_serial_codes(self, vals_list):
        for val in vals_list:
            serial_code = val['serial_code']
            aes_cipher = self.env['aes.cipher'].create([])
            encrypted_serial_code = aes_cipher.encrypt(serial_code)
            val['serial_code'] = encrypted_serial_code
        return vals_list

    def decrypt_serial_code(self):
        aes_cipher = self.env['aes.cipher'].create([])
        return aes_cipher.decrypt(self.serial_code)

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'serial_number': self.serial_number,
            'name': self.product_id.name,
            'image': self.product_id.get_product_image_url(),
            'pulled_by_reference': self.pulled_by.reference,
            'pull_date': datetime.datetime.strftime(self.pull_date, DATETIME_FORMAT) if self.pull_date else False,
            'how_to_use': self.product_id.how_to_use,
            'how_to_use_ar': self.product_id.how_to_use_ar,
            'state': self.state,
            'check_count': self.check_count,
            'last_check_time': datetime.datetime.strftime(self.last_check_time,
                                                          DATETIME_FORMAT) if self.last_check_time else False,
        }

    def process_expired_serials(self):
        try:
            query = """
                UPDATE product_serials
                SET state = '4'
                WHERE id IN (
                    SELECT id
                    FROM product_serials
                    WHERE state IN ('1', '2')
                    AND current_date >= expiry_date
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING id;
            """

            self._cr.execute(query)
            updated_ids = self._cr.fetchall()  # Fetch the IDs of updated rows
            _logger.info(f"Updated rows: {updated_ids}")
            return
        except Exception as e:
            _logger.info("skarla_cron expired serials")
            _logger.exception(e)
            self.env.cr.rollback()
