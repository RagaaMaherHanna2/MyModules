from odoo import models, fields, api, _
from Crypto.Cipher import AES
import base64
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import os
from odoo.tools.config import config


class AESCipher(models.Model):
    _name = 'aes.cipher'

    @staticmethod
    def encrypt(raw):
        key = config.get("encryption_key").encode()
        block_size = AES.block_size  # 16
        raw = pad(raw.encode("UTF-8"), block_size)

        iv = get_random_bytes(AES.block_size)

        cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    @staticmethod
    def decrypt(enc):
        key =config.get("encryption_key").encode()
        unpad = lambda s: s[:-ord(s[-1:])]
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_code = unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf8')
        return decrypted_code
