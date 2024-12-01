from datetime import datetime
from odoo import fields, models, api
import random
import datetime
import math
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT


class PackageCodes(models.Model):
    _name = 'package.codes'
    _description = 'Description'

    code = fields.Char('Mask Code', index=True, unique=True)
    name = fields.Char('PIN Code', index=True, unique=True)
    product = fields.Many2one(
        'product.template', 'Product', index=True, required=True)
    generation_request = fields.Many2one('package.generation.request')
    package = fields.Many2one("package", index=True)

    serial_id = fields.Many2one(
        'product.serials', 'Serial Code')
    reference_user_id = fields.Char('Merchant\'s User ', help='The User Id which provided by the merchant.')
    pull_date = fields.Datetime('Pull Date')
    pulled_by = fields.Many2one("res.users", domain=[('is_merchant', '=', True)], index=True)

    expiry_date = fields.Datetime('Expiry Date')

    redemption_date = fields.Datetime('Redemption Date')

    is_invoiced = fields.Boolean("Is Invoiced", default=False)

    status = fields.Selection([
        ('generated', 'Generated'),
        ('pulled', 'Pulled'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
    ], default='generated', index=True)

    code_type = fields.Selection([
        ('alphanumeric', 'Alphanumeric'),
        ('numeric', 'Numeric'),
        ('alpha', 'Alpha')], default='alphanumeric')
    seperator = fields.Selection([
        ('-', 'Dash (-)'),
        ('nothing', 'Nothing')], default='-')
    parts_count = 4
    parts_lens = [4, 3, 3, 4]
    alphanumeric_symbols_str = '0123456789ABCDEFGHJKLMNPQRTUVWXY'
    alpha_symbols_str = 'ABCDEFGHJKLMNPQRTUVWXY'
    numeric_symbols_str = '0987654321'

    def generate(self):
        symbols_arr = self.get_code_type_symbols()
        code_len = sum(self.parts_lens)
        parts = self.generate_code_parts(self.parts_lens, symbols_arr, code_len)
        if self.has_bad_word(''.join(parts)):
            self.generate()
        else:
            self.code = self.seperator.join(parts) if self.seperator != 'nothing' else ''.join(parts)
            self.generate_pin_code()

    def generate_pin_code(self):
        now = datetime.datetime.now()
        self.name = self.to_hex(now.year, 4) + self.to_hex(now.month, 2) + self.to_hex(now.day, 2) + self.to_hex(
            now.hour, 2) + self.to_hex(now.minute, 2) + self.to_hex(now.second, 2) + self.to_hex(
            math.floor(random.random() * 999999) + 1, 6) + self.to_hex(math.floor(random.random() * 999999) + 1, 6)

    def to_hex(self, number, len):
        return str(hex(number)[2:].zfill(len)[-len:])

    @staticmethod
    def get_bad_words_list():
        bad_words_list = 'SHPX PHAG JNAX JNAT CVFF PBPX FUVG GJNG GVGF SNEG URYY ZHSS QVPX XABO NEFR FUNT GBFF FYHG GHEQ FYNT PENC CBBC OHGG SRPX OBBO WVFZ WVMM CUNG'
        res = ''
        for c in bad_words_list:
            char_code = ord(u'%s' % c) + 13
            ch = char_code if 90 >= char_code else char_code - 26
            res = res + chr(ch)
        return res.split('-')

    def has_bad_word(self, code):
        bad_words_list = self.get_bad_words_list()
        code_upper = code.upper()
        for word in bad_words_list:
            if word in code_upper:
                return True
        return False

    @staticmethod
    def get_random_symbol(symbols_arr):
        random_number = random.random() * len(symbols_arr)
        split_num = str(random_number).split('.')
        int_part = int(split_num[0])
        return symbols_arr[int_part]

    def check_digit_alg(self, data, check, code_len):
        symbols_arr = self.get_code_type_symbols()
        symbols_obj = {}
        for i, symbol in enumerate(symbols_arr):
            symbols_obj[symbol] = i
        for char in data:
            k = symbols_obj[char]
            check = check * (len(symbols_arr) - code_len - 1) + k
        return symbols_arr[check % (len(symbols_arr) - 1)]

    def get_code_type_symbols(self):
        if self.code_type == 'alphanumeric':
            symbols_arr = list(self.alphanumeric_symbols_str)
        elif self.code_type == 'alpha':
            symbols_arr = list(self.alpha_symbols_str)
        else:
            symbols_arr = list(self.numeric_symbols_str)
        return symbols_arr

    def generate_code_parts(self, part_lens, symbols_arr, code_len):
        parts = []
        for i in range(self.parts_count):
            part_code = ''
            for elem in range(part_lens[i] - 1):
                part_code = part_code + self.get_random_symbol(symbols_arr)
            part_code = part_code + self.check_digit_alg(part_code, i + 1, code_len)
            parts.append(part_code)
        return parts

    def get_decrypted_serial_code(self):
        if self.serial_id:
            return self.serial_id.decrypt_serial_code()
        else:
            return False

    def redeem(self):
        self.status = 'redeemed'
        self.redemption_date = datetime.datetime.now()

    def serialize_for_api(self):
        return {
            "pin_code": self.name,
            "code": self.code,
            "product": {
                'id': self.product.id,
                'name_ar': self.product.name_ar,
                'name': self.product.name
            },
            "package": {
                'id': self.package.id,
                'package_name_ar': self.package.package_name_ar,
                'package_name': self.package.package_name
            },
            "creation_date": datetime.datetime.strftime(self.create_date,
                                                        DATETIME_FORMAT) if self.create_date else None,
            "status": self.status,
            "redemption_date": datetime.datetime.strftime(self.redemption_date,
                                                          DATETIME_FORMAT) if self.redemption_date else None,
            "expiry_date": datetime.datetime.strftime(self.expiry_date, DATETIME_FORMAT) if self.expiry_date else None,
            "pull_date": datetime.datetime.strftime(self.pull_date, DATETIME_FORMAT) if self.pull_date else None,
            "reference_user_id": self.reference_user_id if self.reference_user_id else "",
            "pulled_by": {
                'id': self.pulled_by.id,
                'name': self.pulled_by.name,
            } if self.pulled_by else None,
        }
