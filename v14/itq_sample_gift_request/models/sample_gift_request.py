# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SampleGiftRequest(models.Model):
    _name = 'sample.gift.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Request ID', readonly=True)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('confirmed', 'Confirmed'),
                                                        ('manager_approved', 'Manager Approved'),
                                                        ('done', 'Done'),
                                                        ('rejected', 'Rejected'),
                                                        ], default='draft', tracking=True)
    create_date = fields.Datetime(string='Create Date',
                                  default=fields.Datetime.now, )
    effective_date = fields.Date('Effective Date', readonly=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id,
                                domain="[('company_id', '=', company_id)]", tracking=True)
    branch_manager_id = fields.Many2one('res.users', default=lambda self: self.env.user.branch_id.manager_id.user_id)
    warehouse_location_id = fields.Many2one('stock.location', string='Warehouse Location',
                                            domain="[('branch_id', '=', branch_id),('usage', '=', 'internal'),('scrap_location', '=', False)]",
                                            tracking=True, required=True)
    scrap_location_id = fields.Many2one('stock.location', string='Scrap Location',
                                        domain="[('branch_id', '=', branch_id),('scrap_location', '=', True)]",
                                        tracking=True, required=True)
    sample_line_ids = fields.One2many('sample.gift.line', 'sample_id', 'Requested Products', )
    selected_products_ids = fields.Many2many('product.product', compute='_compute_selected_products')

    request_scraps_ids = fields.One2many('stock.scrap', 'sample_id', 'Request Scraps', )
    scraps_count = fields.Integer('Request Scraps Count', compute='_compute_scraps_count')

    description = fields.Text('Description', tracking=True)
    rejection_reason = fields.Text('Rejection Reason')

    can_confirm = fields.Boolean(compute='_compute_can_confirm')
    is_branch_manager = fields.Boolean(compute='_compute_is_branch_manager')
    is_products_limited = fields.Boolean(related="branch_id.apply_sample_limitation")

    @api.model
    def create(self, vals):
        gift_code = self.env['ir.sequence'].next_by_code('sample.gift.seq')
        if 'branch_id' in vals:
            branch = self.env['res.branch'].browse(vals['branch_id'])
            gift_code = branch.code + gift_code
        vals['name'] = gift_code
        res = super(SampleGiftRequest, self).create(vals)
        return res

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            self.update({
                'branch_manager_id': self.branch_id.manager_id.user_id
            })

    def action_archive(self):
        for rec in self:
            if rec.state not in ['draft', 'rejected']:
                raise ValidationError(_("Can archive record in draft or rejected state only."))
            if rec.state == 'done' and rec.branch_id.active:
                raise ValidationError(_("You Cannot archive Done record with active Branch."))
        return super(SampleGiftRequest, self).action_archive()

    def action_unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Cannot Delete record not in draft state."))
        return super(SampleGiftRequest, self).action_unlink()

    def _compute_is_branch_manager(self):
        for rec in self:
            rec.is_branch_manager = self.env.user == rec.branch_id.manager_id.user_id

    def _compute_can_confirm(self):
        for rec in self:
            rec.can_confirm = True if self.state == 'draft' and (
                    self.env.user == self.user_id or self.is_branch_manager) else False

    @api.depends('sample_line_ids', 'warehouse_location_id')
    def _compute_selected_products(self):
        for rec in self:
            selected_products_ids = self.env['product.product'].search([('id', 'in', [])])
            if rec.warehouse_location_id or rec.sample_line_ids:
                location_available_products = self.env['stock.quant'].search(
                    [('location_id', '=', rec.warehouse_location_id.id),
                     ('product_id.tracking', 'in', ['lot', 'serial'])]).filtered(
                    lambda s: s.available_quantity > 0.0).mapped('product_id')
                selected_products_ids = location_available_products - self.sample_line_ids.mapped('product_id')

            rec.selected_products_ids = selected_products_ids

    @api.depends('request_scraps_ids')
    def _compute_scraps_count(self):
        for rec in self:
            rec.scraps_count = len(rec.request_scraps_ids) if rec.request_scraps_ids else 0

    @api.constrains('sample_line_ids')
    def _check_sample_line_ids_limit(self):
        for rec in self:
            if rec.sample_line_ids:
                rec.check_is_exceeded_product_limit()

    def action_confirm_request(self):
        self.check_is_exceeded_product_limit()
        if any(not line.lot_ids for line in self.sample_line_ids):
            raise ValidationError(_('you have to add lot serials for all products!'))
        self.state = 'confirmed'

    def action_approve_request(self):
        self.check_is_exceeded_product_limit()
        self.state = 'manager_approved'

    def action_reject_request(self):
        # self.check_is_exceeded_product_limit()
        view_id = self.env.ref('itq_sample_gift_request.view_rejection_wizard_form').id
        return {
            'name': _('Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'sample.rejection.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }

    def action_done_request(self):
        self.check_is_exceeded_product_limit()
        for line in self.sample_line_ids.mapped('product_serial_lines'):
            scrap_vals = self._prepare_scrap_vals(line)
            scrap = self.env['stock.scrap'].create(scrap_vals)
            scrap.do_scrap()
        self.effective_date = fields.Date.today()
        self.state = 'done'

    def action_view_scraps(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action['domain'] = [('id', 'in', self.request_scraps_ids.ids)]
        return action

    def _prepare_scrap_vals(self, line):
        return {
            'scrap_qty': line.product_qty,
            'product_uom_id': line.product_uom.id,
            'location_id': self.warehouse_location_id.id,
            'scrap_location_id': self.scrap_location_id.id,
            'product_id': line.product_id.id,
            'sample_id': self.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'lot_id': line.lot_id.id,
        }

    def check_is_exceeded_product_limit(self):
        if self.is_products_limited:
            for line in self.sample_line_ids:
                uom = line.product_id.uom_id
                domain = [('branch_id', '=', self.branch_id.id)]
                if line.product_id.variant_sample_limit_ids:
                    domain.append(('product_product_id', '=', line.product_id.id))
                else:
                    domain.append(('product_id', '=', line.product_id.product_tmpl_id.id))
                product_branch_limit = self.env['product.sample.limit'].search(domain)

                if product_branch_limit:
                    product_limit = product_branch_limit.limit_qty
                    product_limit_uom = uom._compute_quantity(product_limit, line.product_uom,
                                                              rounding_method='HALF-UP')
                    month_start = date.today().replace(day=1)
                    month_end = (month_start + relativedelta(months=1, day=1)) - timedelta(1)
                    month_requests_lines = self.env['sample.gift.line'].search(
                        [('product_id', '=', line.product_id.id),
                         ('create_date', '>=', month_start),
                         ('create_date', '<=', month_end),
                         ('sample_id.state', 'in', ['confirmed', 'manager_approved', 'done']),
                         ])
                    month_demanded_uom_qty = 0.0
                    for r_line in month_requests_lines:
                        month_demanded_uom_qty += uom._compute_quantity(r_line.product_qty, r_line.product_uom,
                                                                        rounding_method='HALF-UP')
                    if month_demanded_uom_qty > product_limit_uom:
                        raise ValidationError(
                            _("You Cannot request for product %s because the branch exceeded it's limit" % (
                                line.product_id.name)))
        return True
