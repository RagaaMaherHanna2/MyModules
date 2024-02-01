# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResBranch(models.Model):
    _inherit = 'res.branch'

    has_warehouse = fields.Boolean(string='Has Warehouse')
    warehouse_ids = fields.One2many('stock.warehouse', 'branch_id', string='Warehouses')
    warehouses_count = fields.Integer(string='Warehouse', compute='_compute_warehouses_count')
    has_pos = fields.Boolean(string='Has POS', store=True)
    pos_ids = fields.One2many('pos.config', 'branch_id', string='POSs')
    has_pos_checked = fields.Boolean(string='Has POS Checked')
    pos_count = fields.Integer(string='POS', compute='_compute_pos_count')

    location_ids = fields.One2many('stock.location', 'branch_id', string='Locations')
    locations_count = fields.Integer(string='Warehouse', compute='_compute_locations_count')

    def _compute_pos_count(self):
        for rec in self:
            rec.pos_count = len(rec.pos_ids)

    def _compute_warehouses_count(self):
        for rec in self:
            rec.warehouses_count = len(rec.warehouse_ids)

    def _compute_locations_count(self):
        for rec in self:
            rec.locations_count = self.env['stock.location'].search_count(
                [('branch_id', '=', rec.id)])

    @api.onchange('has_pos')
    def _onchange_has_pos(self):
        if self.has_pos:
            self.has_warehouse = True

    @api.model
    def create(self, vals):
        res = super(ResBranch, self).create(vals)
        dic_values = res.read()[0]
        if vals.get('has_pos'):
            self.env['pos.config'].sudo().create(self._prepare_pos_vals(dic_values))
            res.has_pos_checked = True

        if vals.get('has_warehouse'):
            self.env['stock.warehouse'].sudo().create(self._prepare_warehouse_vals(dic_values))
        self._assign_branch_to_current_user(res)
        return res

    def write(self, vals):
        res = super(ResBranch, self).write(vals)
        for rec in self:
            dic_values = rec.read()[0]
            if 'has_warehouse' in vals and vals['has_warehouse']:
                old_warehouses = self.env['stock.warehouse'].search(
                    [('name', '=', self.name), ('branch_id', '=', self.id),
                     ('company_id', '=', self.company_id.id)])
                if not old_warehouses:
                    self.env['stock.warehouse'].sudo().create(self._prepare_warehouse_vals(dic_values))
            if 'has_pos' in vals and vals['has_pos']:
                self.env['pos.config'].sudo().create(self._prepare_pos_vals(dic_values))
                rec.has_pos_checked = True

            return res

    def unlink(self):
        for rec in self:
            rec.check_record_used("Sorry, You can't delete used Branch record.")
        return super(ResBranch, self).unlink()

    def action_archive(self):
        for rec in self:
            rec._check_branch_pos_has_active_sessions(action='archive')
            rec._check_branch_warehouses_has_active_transfers(action='archive')
            rec.pos_ids.sudo().action_archive()
            rec.warehouse_ids.sudo().action_archive()
        return super(ResBranch, self).action_archive()

    def action_unarchive(self):
        res = super(ResBranch, self).action_unarchive()
        self._assign_branch_to_current_user(self)
        return res

    def _assign_branch_to_current_user(self, res):
        self.env.user.branch_ids |= res

    @staticmethod
    def _prepare_warehouse_vals(vals):
        return {
            'name': vals['name'],
            'company_id': int(vals['company_id'][0]),
            'code': vals['code'],
            'branch_id': vals['id'] if vals['id'] else False,
        }

    @staticmethod
    def _prepare_pos_vals(vals):
        return {
            'name': vals['name'],
            'company_id': int(vals['company_id'][0]),
            'branch_is_set': True,
            'image': vals['image_1920'],
            'branch_id': vals['id'] if vals['id'] else False,
        }

    def _check_branch_pos_has_active_sessions(self, action):
        if self.pos_ids.filtered(lambda p: p.has_active_session):
            raise ValidationError(_('You cannot %s Branch has related pos with active sessions!') % _(action))

    def _check_branch_warehouses_has_active_transfers(self, action):
        if self.env['stock.picking'].search(
                [('branch_id', '=', self.id)]).filtered(lambda p: p.state not in ['done', 'cancel']):
            raise ValidationError(_('You cannot %s Branch has related warehouse with active pickings!') % _(action))

    def action_open_pos_configs(self):
        action = self.env.ref('point_of_sale.action_pos_config_kanban').read([])[0]
        action['domain'] = [('id', 'in', self.pos_ids.ids)]
        return action

    def action_open_warehouses(self):
        action = self.env.ref('stock.action_warehouse_form').read([])[0]
        action['domain'] = [('id', 'in', self.warehouse_ids.ids)]
        return action

    def action_open_locations(self):
        action = self.env.ref('stock.action_location_form').read([])[0]
        action['domain'] = [('id', 'in', self.location_ids.ids)]
        return action
