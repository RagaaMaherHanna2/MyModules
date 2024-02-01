# -*- coding: utf-8 -*-
import base64
import struct
import sys
from datetime import datetime, timedelta

from odoo import fields, http, _, tools
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request, _logger
from odoo.osv import expression
from odoo.tools.misc import get_lang
from odoo.tools import lazy
from odoo.exceptions import UserError, ValidationError


class visitRequestController(http.Controller):

    def sitemap_visit(env, rule, qs):
        if not qs or qs.lower() in '/visit_requests':
            yield {'loc': '/visit_requests'}

    # ------------------------------------------------------------
    # visit LIST
    # ------------------------------------------------------------

    @http.route(['/search/my/visit_requests'], type='http', auth="public", website=True)
    def search_my_visit_requests(self):
        visit_request = request.env['itq.visit.request']
        values = {}
        return request.render("itq_event_portal.portal_search_my_visit_requests_template", values)

    @http.route(
        ['/my/visit_request', '/my/visit_request/page/<int:page>', '/my/visit_requests',
         '/my/visit_requests/page/<int:page>'],
        type='http', auth="public",
        website=True, sitemap=sitemap_visit)
    def my_visit_requests(self, page=1, **kwargs):
        name = kwargs['request_number']
        phone_number = kwargs['phone_number']
        my_visit_request = request.env['itq.visit.request'].sudo().search([('name', '=', name),
                                                                           ('phone_number', '=', phone_number)])

        pager = request.website.pager(
            url="/visit_requests",
            total=len(my_visit_request),
            page=page,
            step=6,
            scope=5)
        values = {
            'visit_requests': my_visit_request,
            'pager': pager,
            'search_count': len(my_visit_request),
        }
        return request.render("itq_event_portal.portal_requests_list_template", values)

    @http.route(
        ['/visit_request', '/visit_request/page/<int:page>', '/visit_requests', '/visit_requests/page/<int:page>'],
        type='http', auth="public",
        website=True, sitemap=sitemap_visit)
    def visit_requests(self, page=1, **searches):
        visit_request = request.env['itq.visit.request']

        searches.setdefault('search', '')
        website = request.website

        step = 12  # Number of events per page

        options = {
            'displayDescription': False,
            'displayDetail': False,
            'displayExtraDetail': False,
            'displayExtraLink': False,
            'displayImage': False,
            'allowFuzzy': not searches.get('noFuzzy'),
        }
        order = 'name'
        search = searches.get('search')
        v_request_count, details, fuzzy_search_term = website.sudo()._search_with_fuzzy("visit_requests", search,
                                                                                        limit=page * step, order=order,
                                                                                        options=options)
        v_request_details = details[0]
        v_requests = v_request_details.get('results', visit_request)
        v_requests = v_requests[(page - 1) * step:page * step]

        # if v_requests and searches['request_number'] and searches['phone_number']:
        #     v_requests.filtered(lambda r: r.name ==  searches['request_number'] and r.phone_number == searches['phone_number'])

        pager = website.pager(
            url="/visit_request",
            url_args=searches,
            total=len(v_requests),
            page=page,
            step=step,
            scope=5)
        print('searches', searches)
        print('search', search)
        keep = QueryURL('/visit_request', **{
            key: value for key, value in searches.items()})

        searches['search'] = fuzzy_search_term or search

        values = {
            'visit_requests': v_requests,  # event_ids used in website_event_track so we keep name as it is
            'pager': pager,
            'searches': searches,
            'keep': keep,
            'search_count': v_request_count,
            'original_search': fuzzy_search_term and search,
        }
        return request.render("itq_event_portal.portal_requests_list_template", values)

    def prepare_request_values_for_portal(self):
        visitor_organizations = request.env['itq.organization.type'].sudo().search([('state', '=', 'active')])
        visit_classifications = request.env['itq.visit.classification'].sudo().search([('state', '=', 'active')])
        attractions = request.env['itq.attraction.location'].sudo().search([('state', '=', 'active')])
        departments = request.env['hr.department'].sudo().search([('is_visitable', '=', True)])
        research_types = request.env['itq.research.type'].sudo().search([('state', '=', 'active')])
        documentation_types = request.env['itq.documentation.type'].sudo().search([('state', '=', 'active')])

        return {
            'visitor_organizations': visitor_organizations,
            'visit_classifications': visit_classifications,
            'visit_attractions': attractions.filtered(lambda a: a.is_visit),
            'photoshoot_attractions': attractions.filtered(lambda a: a.is_photo_shoot),
            'departments': departments,
            'research_types': research_types,
            'documentation_types': documentation_types,
        }

    @http.route(['''/visit_request/<model("itq.visit.request"):visit_request>'''], type='http', auth="public",
                website=True, sitemap=True)
    def visit_request(self, visit_request, **post):
        values = {'visit_request': visit_request}
        values.update(self.prepare_request_values_for_portal())
        return request.render("itq_event_portal.portal_to_visit_request_template", values)

    @http.route(['/to_visit_request'], type='http', auth="public", website=True)
    def to_visit_request(self, **kwargs):
        form_values = self.prepare_request_values_for_portal()
        return request.render("itq_event_portal.portal_to_visit_request_template", form_values)

    def _prepare_visit_request_values_from_portal(self, form_details):
        request_fields = {key: v for key, v in request.env['itq.visit.request']._fields.items()}
        request_values = {}
        for key, value in form_details.items():
            field_name = key
            if field_name not in request_fields :
                if field_name in ['visit_attraction_id', 'photoshoot_attraction_id']:
                    value = int(value) if value else False
                    field_name = 'to_visit_attraction_id'
                else:
                    continue
            elif isinstance(request_fields[field_name], (fields.Many2one)):
                value = int(value) if value else False

            elif field_name == 'visit_letter_id':
                try:
                    value = base64.b64decode(value)
                    value = base64.b64encode(value)
                except Exception as e:
                    _logger.warning("Attachment Creating Error: %s" % e)

            elif field_name == 'visit_document':
                value = True if value == 'on' else False

            elif isinstance(request_fields[field_name], (fields.Datetime)):
                try:
                    value = datetime.strptime(value, '%m/%d/%Y %H:%M %p')
                except Exception:
                    pass

            request_values.update({
                field_name: value
            })
        return request_values

    @http.route(['/visit_request_create'], type='json', auth="public", website=True)
    def visit_request_create(self, **params):
        prepared_values = self._prepare_visit_request_values_from_portal(params['req_values'])
        new_req = request.env['itq.visit.request'].sudo().with_context({'default_request_source': 'external'}).create(
            prepared_values)
        new_req.submit_to_review()
        return new_req.get_portal_url()

    @http.route(['/visit_request_update'], type='json', auth="public", website=True)
    def visit_request_update(self, **params):
        prepared_values = self._prepare_visit_request_values_from_portal(params['req_values'])
        updated_req = request.env['itq.visit.request'].browse(int(params['visit_request_id']))
        updated_req.sudo().write(prepared_values)
        if updated_req.state == 'draft':
            updated_req.submit_to_review()
        return updated_req.get_portal_url()