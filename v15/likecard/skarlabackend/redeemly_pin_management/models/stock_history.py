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


class StockHistory(models.Model):
    _name = 'serials.stock.history'
    _rec_name = 'product_id'

    history_date = fields.Datetime(string='Date')
    product_id = fields.Many2one('product.template')

    total = fields.Float(string='Total')
    available = fields.Float(string='available')
    pulled = fields.Float(string='pulled')
    frozen = fields.Float(string='frozen')


    def serialize_for_api(self):
        self.ensure_one()
        return {
            'history_date': datetime.datetime.strftime(self.history_date, DATETIME_FORMAT),
            'product': {'id': self.product_id.id,
                        'name': self.product_id.name
                        },
            'total': self.total,
            'available': self.available,
            'pulled': self.pulled,
            'frozen': self.frozen
        }

    def collect_on_hand_qty_snapshots(self):
        products = self.env['product.template'].search([('enable_stock_history', '=', True),
                                                        ("is_redeemly_product", "=", True)
                                                        ])
        for product in products:
            self.env['serials.stock.history'].create({
                'history_date': datetime.datetime.now(),
                'product_id': product.id,
                'total': self.env['product.serials'].search_count([('product_id', '=', product.id)]),
                'available': product.get_product_actual_stock(),
                'pulled': product.get_product_redeemed_stock(),
                'frozen': self.env['product.serials'].search_count(
                    [('state', '=', '1'), ('product_id', '=', product.id), ('batch_id.state', '=', '2')]),
            })
