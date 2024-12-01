import datetime
import itertools

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT


class PackageGenerationRequest(models.Model):
    _name = 'package.generation.request'
    _description = 'Generation Requests'

    state = fields.Selection(
        [('pending', 'Pending'), ("success", 'Success'), ('failed', 'Failed'), ('canceled', 'Canceled')],
        string='Status', readonly=True, copy=False, index=True, tracking=3, default='pending')
    lines = fields.One2many(
        comodel_name='package.generation.request.line', inverse_name="generation_request")
    codes = fields.One2many(
        comodel_name='package.codes', inverse_name="generation_request")
    serials = fields.One2many(comodel_name='product.serials', inverse_name="generation_request_id")
    package = fields.Many2one(
        comodel_name='package', required=True, ondelete='cascade')

    start_time = fields.Datetime("Started At")
    end_time = fields.Datetime("Finished At")
    fail_message = fields.Char("Fail Reason")

    def serialize_for_api(self):
        return {
            "id": self.id,
            "package": self.package.name,
            "state": self.state,
            "fail_message": self.fail_message if self.fail_message else "",
            'start_time': datetime.datetime.strftime(self.start_time, DATETIME_FORMAT) if self.start_time else None,
            'end_time': datetime.datetime.strftime(self.end_time, DATETIME_FORMAT) if self.end_time else None,
            'create_date': datetime.datetime.strftime(self.create_date, DATETIME_FORMAT) if self.create_date else None,
            'lines': [
                {
                    'product': {
                        'id': line.product.id,
                        'name': line.product.name,
                        'name_ar': line.product.name_ar,
                    },
                    'quantity': line.quantity
                }
                for line in self.lines
            ]
        }

    def process_pending_requests(self):
        pending_requests = self.search([('state', '=', 'pending')], order="create_date")
        limit = config.get("generation_limit_per_batch", 10)
        processed_requests_count = 0
        for generation_request in pending_requests:
            processed_requests_count += 1
            if processed_requests_count > limit:
                break
            try:
                generation_request.start_time = datetime.datetime.now()
                for line in generation_request.lines:
                    # codes = []
                    # for index in range(line.quantity):
                    #     code = self.env['package.codes'].create({
                    #         'status': 'generated',
                    #         'product': line.product.id,
                    #         'generation_request': generation_request.id,
                    #         'package': generation_request.package.id,
                    #         'code_type': generation_request.package.code_type,
                    #         'seperator': generation_request.package.code_seperator,
                    #     })
                    #     code.generate()
                    #     codes.append(code)
                    if line.product.has_serials:
                        self._reserve_serials_without_codes(line.quantity, line.product, line.generation_request)
                generation_request.state = 'success'
                generation_request.end_time = datetime.datetime.now()
            except Exception as ex:
                self.env.cr.rollback()
                generation_request.start_time = datetime.datetime.now()
                generation_request.end_time = datetime.datetime.now()
                generation_request.state = 'failed'
                generation_request.fail_message = str(ex)

    def _reserve_serials(self, codes, product):
        self._cr.execute(""" WITH req AS (
                                            SELECT id
                                              FROM product_serials
                                             WHERE state = '1'
                                             and product_id = %s
                                             order by expiry_date
                                                limit %s
                                            FOR UPDATE SKIP LOCKED
                                        )
                                        UPDATE product_serials AS rs
                                           SET state = '2'
                                          FROM req
                                         WHERE rs.id = req.id
                                         RETURNING rs.ID;
                                        """,
                         [product.id, len(codes)])

        serial_ids = self._cr.fetchall()
        if len(serial_ids) < len(codes):
            raise ValidationError("Not Enough Stock For Product %s" % product.name)

        for (_id, code) in itertools.zip_longest(serial_ids, codes):
            code.serial_id = _id

    def _reserve_serials_without_codes(self, quantity, product, generation_request_id):
        self._cr.execute(""" WITH req AS (
                                            SELECT id
                                              FROM product_serials
                                             WHERE state = '1'
                                             and product_id = %s
                                             order by expiry_date
                                                limit %s
                                            FOR UPDATE SKIP LOCKED
                                        )
                                        UPDATE product_serials AS rs
                                           SET state = '2',
                                           generation_request_id = %s
                                          FROM req
                                         WHERE rs.id = req.id
                                         RETURNING rs.ID;
                                        """,
                         [product.id, quantity, generation_request_id.id])

        serial_ids = self._cr.fetchall()
        if len(serial_ids) < quantity:
            raise ValidationError("Not Enough Stock For Product %s" % product.name)

        # for (_id, code) in itertools.zip_longest(serial_ids, codes):
        #     code.serial_id = _id


class PackageGenerationRequestLine(models.Model):
    _name = 'package.generation.request.line'
    _description = 'Generation Request Lines'

    product = fields.Many2one('product.template', string='Product', required=True,
                              domain=[('is_redeemly_product', '=', True)])

    quantity = fields.Integer("Quantity", required=True)

    generation_request = fields.Many2one(
        comodel_name='package.generation.request', ondelete="cascade")
