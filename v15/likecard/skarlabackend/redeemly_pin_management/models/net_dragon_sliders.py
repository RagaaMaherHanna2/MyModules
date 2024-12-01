from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.config import config
import calendar


class NetDragonRedmptionPortalSlider(models.Model):
    _name = 'netdragon.slider'

    title = fields.Char(stirng='Title')
    image = fields.Binary(string='Image')
    image_file_name = fields.Char(string='Image Filename')
    image_url = fields.Char(string='Image URL', compute="compute_image_url")
    product_id = fields.Many2one('product.template')

    @api.onchange("image")
    def compute_image_url(self):
        for rec in self:
            attachment = self.env['ir.attachment'].search(
                [("res_model", "=", "netdragon.slider"), ('res_id', '=', rec.id),
                 ('res_field', '=', 'image')])
            if attachment:
                rec.image_url = attachment[0].url
            else:
                rec.image_url = ""

    def serialize_for_api(self):
        return {
            'title': self.title,
            'image_url': self.image_url,
            "product_id": False,
            'product_name': False
        }


class NetDragonProductCategory(models.Model):
    _name = 'netdragon.product.category'

    name = fields.Char(string='Category Name')
    sku = fields.Char(string='Netdragon SKU')
    endpoint = fields.Char(string='Netdragon Endpoint')
    image = fields.Binary(string='Image')
    image_file_name = fields.Char(string='Image Filename')
    image_large = fields.Binary(string='Large Image')
    image_large_file_name = fields.Char(string='Image Filename Large')
    image_url = fields.Char(string='Image URL', compute="compute_image_url")
    image_url_large = fields.Char(string='Image URL', compute="compute_image_url")

    @api.onchange("image", "image_large")
    def compute_image_url(self):
        for rec in self:
            attachment = self.env['ir.attachment'].search(
                [("res_model", "=", "netdragon.product.category"), ('res_id', '=', rec.id),
                 ('res_field', '=', 'image')])
            attachment2 = self.env['ir.attachment'].search(
                [("res_model", "=", "netdragon.product.category"), ('res_id', '=', rec.id),
                 ('res_field', '=', 'image_large')])
            if attachment and attachment2:
                rec.image_url = attachment[0].url
                rec.image_url_large = attachment2[0].url
            else:
                rec.image_url = ""
                rec.image_url_large = ""

    def serialize_for_api(self):
        return {
            'name': self.name,
            'id': self.id,
            'image': self.image_url,
            'image_url_large': self.image_url_large,
        }