from odoo import fields, models, registry


class RunningOps(models.Model):
    _name = 'running.ops'
    _description = 'Running Operations'

    type = fields.Selection([(
        "redeem", 'redeem'
    )])
    unique_val = fields.Char()

    _sql_constraints = [('unique_val_unique', 'unique(unique_val)',"Another operation is running. please wait")]

    def add_entry(self, vals):
        self.flush()  # ADDED WITH IMPORTANT EDIT BELOW
        with registry(self.env.cr.dbname).cursor() as cr:
            record = self.with_env(self.env(cr)).create(vals)
            return self.browse(record.id)

    def remove_entry(self, entry_id):
        self.flush()  # ADDED WITH IMPORTANT EDIT BELOW
        with registry(self.env.cr.dbname).cursor() as cr:
            self.with_env(self.env(cr)).search([("id", "=", entry_id)]).unlink()
