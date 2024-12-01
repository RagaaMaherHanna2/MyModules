import json
import logging

from odoo.tools import config
from odoo.exceptions import UserError
import requests
import secrets
logger = logging.getLogger(__name__)

class BabelVoucherService:
    @staticmethod
    def send_generated_codes(codes: [], sku, distributor, country_of_generation_parameters):
        if len(codes) == 0:
            return
        data = {"codes": codes, "sku": sku, "distributor": distributor, "country_of_generation_parameters": country_of_generation_parameters}
        logger.info("#########data - %s", data)
        payload = json.dumps(data)

        headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": config.get("babel_key_integ")}
        call_back_endpoint = config.get('babel_callback')
        r = requests.post(url=call_back_endpoint, data=payload, headers=headers)
        if r.status_code == 200:
            return
        else:
            raise UserError(r.json())

    @staticmethod
    def generate_secret_key():
        return secrets.token_hex(32)
