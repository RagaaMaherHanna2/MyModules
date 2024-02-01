from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeChecklist(models.Model):
    _inherit = 'itq.employee.checklist'

    checklist_exit_type = fields.Selection(selection_add=[('petty_cash', 'Petty Cash')],
                                           ondelete={'petty_cash': 'set default'})

    def _compute_is_checklist_readonly(self):
        super(EmployeeChecklist, self)._compute_is_checklist_readonly()
        for rec in self:
            if rec.checklist_exit_type == 'petty_cash':
                rec.is_checklist_readonly = True

    def action_archive(self):
        for rec in self:
            if rec.checklist_exit_type == 'petty_cash':
                raise ValidationError(_("Can't Archive Pytty Cash Checklist."))
        return super(EmployeeChecklist, self).action_archive()

    def unlink(self):
        for rec in self:
            if rec.checklist_exit_type == 'petty_cash':
                raise ValidationError(_("Can't Delete Pytty Cash Checklist."))
        return super(EmployeeChecklist, self).unlink()
