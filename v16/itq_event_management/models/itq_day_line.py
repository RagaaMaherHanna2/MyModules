from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ItqDayLine(models.Model):
    _name = "itq.day.line"
    _description = 'Day Line'

    name = fields.Integer()

    @api.constrains('name')
    def constraint_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name),
                                  ('id', '!=', rec.id)]):
                raise ValidationError(_('You cannot duplicate {}').format(rec.name))

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} (#{})".format(_("day "), str(record.name) or '')))
        return result

    @api.model
    def create_day_line(self):
        days = []
        for day in range(1, 100):
            days.append({'name': day})
        self.sudo().create(days)
