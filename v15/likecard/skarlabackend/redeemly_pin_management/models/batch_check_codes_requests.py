import datetime
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo.tools import config
from hashlib import sha256


class BatchCheckCodesRequest(models.Model):
    _name = 'batch.check.codes.request'
    _description = 'Check Code Request'

    request_date = fields.Datetime(stirng='Request Date', required=True, default=datetime.datetime.now())
    state = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='pending')
    user_id = fields.Many2one('res.users')
    failure_reason = fields.Char(string='Failure Reason')
    serials = fields.One2many('batch.check.codes.serials', inverse_name='request_id')
    processed_count = fields.Integer(string='Processed Count')

    def process_pending_request(self):
        requests = self.search([('state', '=', 'pending')], order="create_date")
        limit_per_batch = config.get("generation_limit_per_batch", 10)
        aes_cipher = self.env['aes.cipher'].create([])
        for request in requests:
            request_processed_count = 0
            for serial in requests.serials.filtered(lambda v: not v.processed):
                if request_processed_count > limit_per_batch:
                    request.processed_count = requests.processed_count + request_processed_count
                    break
                exist = request.env['product.serials'].with_user(1).search(
                    ['|', ('serial_code_hash', '=', sha256(serial.serial_code.encode('utf-8')).hexdigest()),
                     ('serial_number', '=', serial.serial_code)
                     ])
                if (not exist) or (requests.user_id.is_service_provider and exist.product_id.service_provider_id.id != requests.user_id.id)\
                        or (requests.user_id.is_merchant and exist.pulled_by.id != requests.user_id.id):
                    serial.found = False
                    serial.expired = False
                    serial.expiry_date = False
                elif (exist.expiry_date and exist.expiry_date < datetime.now().date()) or exist.state == '4':
                    serial.found = True
                    serial.expired = True
                    serial.expiry_date = datetime.strftime(serial.expiry_date,
                                                          DATETIME_FORMAT) if serial.expiry_date else None,
                else:
                    serial.serial_number = exist.serial_number
                    serial.name = exist.product_id.name
                    serial.product_type = 'prepaid' if exist.product_id.is_prepaid else 'serial'

                    serial.found = True
                    serial.expired = datetime.now().date() >= serial.expiry_date if serial.expiry_date else False,
                    serial.expiry_date = datetime.strftime(serial.expiry_date, DATETIME_FORMAT) if serial.expiry_date else False,
                    serial.image = exist.product_id.get_product_image_url()
                    serial.pulled_by_reference = exist.pulled_by.reference
                    serial.pull_date = datetime.strftime(exist.pull_date, DATETIME_FORMAT) if exist.pull_date else None
                    serial.how_to_use = exist.product_id.how_to_use
                    serial.how_to_use_ar = exist.product_id.how_to_use_ar
                    exist.check_count = exist.check_count + 1
                    serial.check_count = exist.check_count
                    serial.last_check_time = datetime.strftime(exist.last_check_time,
                                                          DATETIME_FORMAT) if exist.last_check_time else None
                serial.processed = True

                request_processed_count += 1
            if len(request.serials.filtered(lambda v: not v.processed)) == 0:
                request.state = 'success'

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'id': self.id,
            'date': datetime.datetime.strftime(self.request_date, DATETIME_FORMAT),
            'state': self.state,
            'failure_reason': self.failure_reason,
            'processed_count': self.processed_count
        }


class BatchCheckCodesSerials(models.Model):
    _name = 'batch.check.codes.serials'
    _description = 'Check Code Result'

    serial_code = fields.Char(string='Serial Code', required=True, unique=True)
    serial_number = fields.Char(string='Serial Number')
    found = fields.Boolean('Serial Found')
    expired = fields.Boolean('Serial Expired')
    expiry_date = fields.Datetime('Expiration Date')
    name = fields.Char(string='Product Name')
    product_type = fields.Char(string='Product Type')
    image = fields.Char(string='Image')
    pulled_by_reference = fields.Char(string='Pulled By Reference')
    pull_date = fields.Datetime(string='Pull Date')
    how_to_use = fields.Char('How To Use')
    how_to_use_ar = fields.Char('How To Use Arabic')
    check_count = fields.Integer(string='Check Count')
    last_check_time = fields.Datetime(string='Check Date')
    request_id = fields.Many2one('batch.check.codes.request')
    processed = fields.Boolean(string='Processed')

    def serialize_for_api(self):
        self.ensure_one()
        return {
            'serial_code': self.serial_code,
            'serial_number': self.serial_number,
            'found': self.found,
            'type': self.product_type,
            'expired': self.expired,
            'expiry_date': datetime.datetime.strftime(self.expiry_date, DATETIME_FORMAT) if self.expiry_date else None,
            'name': self.name,
            'pulled_by_reference': self.pulled_by_reference,
            'pull_date': datetime.datetime.strftime(self.pull_date, DATETIME_FORMAT) if self.pull_date else None,
            'how_to_use': self.how_to_use,
            'how_to_use_ar': self.how_to_use_ar,
            'check_count': self.check_count,
            'last_check_time': datetime.datetime.strftime(self.last_check_time, DATETIME_FORMAT) if self.last_check_time else None,
        }
