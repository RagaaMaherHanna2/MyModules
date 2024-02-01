from datetime import datetime, timedelta
import re
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError
from phonenumbers import parse, is_valid_number, NumberParseException
from datetime import timedelta
from lxml import etree
import json


class VisitRequest(models.Model):
    _name = "itq.visit.request"
    _inherit = ['itq.visit.request',
                'portal.mixin',
                'website.searchable.mixin', ]

    # EXTENDS portal portal.mixin
    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = '/visit_request/%s' % (rec.id)

    @api.model
    def _search_get_detail(self, website, order, options):
        print('options', options)
        search_fields = ['name', 'phone_number']
        fetch_fields = ['id', 'name', 'phone_number']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'phone_number': {'name': 'phone_number', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
        }
        return {
            'model': 'itq.visit.request',
            'base_domain': [],
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss-square',
            'order': 'name desc, id desc' if 'name desc' in order else 'name asc, id desc',
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(fetch_fields, mapping, icon, limit)
        for data in results_data:
            data['url'] = '/visit_request/%s' % data['id']
        return results_data