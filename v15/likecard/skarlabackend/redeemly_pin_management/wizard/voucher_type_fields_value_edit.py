from odoo import api, fields, models, _


class VoucherFieldsValueEditor(models.TransientModel):
    _name = 'voucher.type.fields.value.edit'

    json_value = fields.Text('Fields Value As Json')