from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    automate_deferred_revenue = fields.Selection([('no', 'No'),
                                                  ('create_in_draft', 'Create in draft'),
                                                  ('create_and_validate', 'Create and validate')], default='no')
    # TODO waiting Hamouda
    # TODO to be M2O
    deferred_revenue_type_id = fields.Char()
    is_current_liabilities = fields.Boolean(compute='compute_account_types')

    automate_deferred_expense = fields.Selection([('no', 'No'),
                                                  ('create_in_draft', 'Create in draft'),
                                                  ('create_and_validate', 'Create and validate')], default='no')
    # TODO waiting Hamouda
    # TODO to be M2O
    deferred_expense_type_id = fields.Char()
    is_current_assets = fields.Boolean(compute='compute_account_types')

    @api.depends('user_type_id')
    def compute_account_types(self):
        for rec in self:
            is_current_liabilities = is_current_assets = False
            if rec.user_type_id:
                if rec.user_type_id == self.env.ref('account.data_account_type_current_liabilities'):
                    is_current_liabilities = True
                if rec.user_type_id == self.env.ref('account.data_account_type_current_assets'):
                    is_current_assets = True
            rec.is_current_liabilities = is_current_liabilities
            rec.is_current_assets = is_current_assets







