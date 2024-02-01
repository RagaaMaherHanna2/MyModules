# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
import re
from phonenumbers import parse, is_valid_number, NumberParseException


class ItqAbstractValidateFieldFormat(models.AbstractModel):
    _name = 'itq.abstract.validate.field.format'

    @api.model
    def _validate_phone_number(self, phone_number):
        try:
            number = parse(phone_number)
            if not is_valid_number(number):
                return False
            return True
        except NumberParseException:
            return False

    @api.model
    def _validate_email(self, email):
        regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        return bool(re.match(regex, email))