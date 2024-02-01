from odoo import models, fields, _, api
import base64
from io import BytesIO
from odoo.exceptions import UserError, ValidationError
import pandas as pd


def is_nan_string(val):
    try:
        float_val = float(val)
        return pd.isna(float_val)
    except ValueError:
        return False


class ItqInviteeWizard(models.TransientModel):
    _name = "itq.invitee.wizard"

    invitee_file = fields.Binary(string="File", required=True, tracking=True)
    event_request_id = fields.Many2one('itq.event.request', default=lambda self: self.get_event_request_id(),
                                       ondelete='cascade', tracking=True)

    @api.model
    def get_event_request_id(self):
        active_id = self.env.context.get('active_id', False)
        return active_id

    def save_data(self):
        self.ensure_one()

        try:
            data = BytesIO(base64.b64decode(self.invitee_file))
            df = pd.read_excel(data)
        except Exception:
            raise UserError(_("please check your file format"))

        # save data
        for index, record in df.iterrows():
            for column in df.columns:
                if is_nan_string(record[column]):
                    record[column] = ""
            try:
                self.env['itq.invitee'].create({
                    'name': record[0],
                    'mobile': record[1],
                    'nationality': record[2],
                    'email': record[3],
                    'identification': record[4],
                    'event_request_id': self.event_request_id.id,
                })
            except Exception as e:
                raise ValidationError(_(e))
