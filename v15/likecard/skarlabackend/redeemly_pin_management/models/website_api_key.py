from odoo import models, fields, api, _
from odoo.api import ondelete


class WebsiteApiKey(models.Model):
    _name = 'website.api.key'

    name = fields.Char(string="Website Name")
    website_redeemly_api_key = fields.Char(string="WEBSITE SKARLA API KEY", unique=True, readonly=True)
    user_id = fields.Many2one('res.users', readonly=True, ondelete='cascade')

    def serialize_for_api(self, id=False):
        return {
            'id': self.id,
            'name': self.name,
            'website_redeemly_api_key': self.website_redeemly_api_key,
            'user_id': self.user_id.id
        }

    @api.model
    def create(self, vals):
        res = super(WebsiteApiKey, self).create(vals)
        res.website_redeemly_api_key =res.user_id.generate_api_key()
        return res