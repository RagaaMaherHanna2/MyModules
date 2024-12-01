import uuid
import datetime
from odoo import models, fields, api, _
from odoo.addons.redeemly_pin_management.constants import DATETIME_FORMAT


class RedeemlyPackage(models.Model):
    _name = 'package'
    _description = 'Packages For Sale'
    _rec_name = "package_name"

    name = fields.Char(string='Reference', copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    package_name = fields.Char("Package Name", required=True, translate=True)
    package_name_ar = fields.Char(string='Name in arabic')

    state = fields.Selection(
        [('draft', 'Draft'), ("published", 'Published'), ('closed', 'Closed'), ('expired', 'Expired')],
        string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    code_type = fields.Selection([
        ('alphanumeric', 'Alphanumeric'),
        ('numeric', 'Numeric'),
        ('alpha', 'Alpha')], default='alphanumeric', required=True)
    code_seperator = fields.Selection([
        ('-', 'Dash (-)'),
        ('nothing', 'Nothing')], default='-', required=True)
    expiry_date = fields.Datetime('Expiration Date')
    code_hours_duration = fields.Integer(string='Codes Duration Hours', default=0)
    code_days_duration = fields.Integer(string='Codes Duration Days', default=90)
    code_duration_minutes = fields.Integer(string='Code Duration', compute="_compute_code_duration_in_minutes")
    service_provider_id = fields.Many2one('res.users', string='Service Provider', required=True,
                                          domain=[('is_service_provider', '=', True)])
    invoicing_policy = fields.Selection([('pulled', 'Based on Pulled Codes'), ('redeemed', 'Based on Redeemed Codes')],
                                        string="Invoicing Policy", default='pulled', required=True)

    generation_requests = fields.One2many(
        comodel_name='package.generation.request', inverse_name="package")

    generated_codes = fields.One2many(
        'package.codes', inverse_name="package"
    )

    generated_codes_count = fields.Integer("Generated Codes", compute="_compute_generated_codes_count")
    reserved_serial_count = fields.Integer("Generated Codes", compute="_compute_reserved_serial_count")
    pulled_codes_count = fields.Integer("Pulled Codes", compute="_compute_pulled_codes_count")

    merchant_invites = fields.One2many(
        comodel_name='merchant.package.invites', inverse_name="product")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = str(uuid.uuid4()).replace("-", '')
        return super(RedeemlyPackage, self).create(vals)

    @api.depends('code_hours_duration', 'code_days_duration')
    def _compute_code_duration_in_minutes(self):
        for rec in self:
            rec.code_duration_minutes = (rec.code_days_duration * 24 * 60) + (rec.code_hours_duration * 60)

    def _compute_pulled_codes_count(self):
        for rec in self:
            rec.pulled_codes_count = self.env['package.codes'].search_count(
                [('package', '=', rec.id), ("status", '=', 'pulled')])

    def _compute_generated_codes_count(self):
        for rec in self:
            rec.generated_codes_count = len(rec.generated_codes)

    def _compute_reserved_serial_count(self):
        for rec in self:
            rec.reserved_serial_count = self.env['product.serials'].search_count([('generation_request_id.package', '=', self.id),
                                                                            ('state', '=', 2)
                                                                            ])


    def publish_package(self):
        self.state = 'published'

    def unpublish_package(self):
        self.state = 'draft'

    def close_package(self):
        self.state = 'closed'

    def show_generation_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("redeemly_pin_management.action_package_generation_request")
        generation_requests = self.generation_requests
        action['domain'] = [('id', 'in', generation_requests.ids)]
        action['context'] = dict(self._context, default_package=self.id)
        return action

    def show_package_codes(self):
        action = self.env["ir.actions.actions"]._for_xml_id("redeemly_pin_management.action_package_codes")
        generated_codes = self.generated_codes
        action['domain'] = [('id', 'in', generated_codes.ids)]
        action['context'] = dict(self._context, default_package=self.id)
        return action

    def show_merchant_invites(self):
        action = self.env["ir.actions.actions"]._for_xml_id("redeemly_pin_management.action_merchant_package_invites")
        merchant_invites = self.merchant_invites
        action['domain'] = [('id', 'in', merchant_invites.ids)]
        action['context'] = dict(self._context, default_package=self.id)
        return action

    def get_products(self):
        grouped = self.env['package.generation.request.line'].with_user(1).read_group(
            [('generation_request', 'in', self.generation_requests.ids)],
            ["product", "quantity:sum"], ['product'])

        products = [
            {
                "product": self.env['product.template'].browse(p["product"][0]),
                "quantity": p['quantity'],
            }
            for p in grouped
        ]

        return products

    def serialize_for_api(self, populate=False):
        package = {
            'reference': self.name,
            'package_name': self.package_name,
            'package_name_ar': self.package_name_ar if self.package_name_ar else "",
            "state": self.state,
            # "code_type": self.code_type,
            # "code_seperator": self.code_seperator,
            "expiry_date": datetime.datetime.strftime(self.expiry_date, DATETIME_FORMAT) if self.expiry_date else None,
            # "code_hours_duration": self.code_hours_duration,
            # "code_days_duration": self.code_days_duration,
            "invoicing_policy": self.invoicing_policy,
            # "generated_codes_count": self.generated_codes_count,
        }

        if populate:
            package["generation_requests"] = [
                request.serialize_for_api()
                for request in self.generation_requests
            ]
            package["merchant_invites"] = [
                invite.serialize_for_api()
                for invite in self.merchant_invites
            ]
            package["products"] = [
                {
                    "id": item['product'].id,
                    "name": item['product'].name,
                    "name_ar": item['product'].name_ar,
                    "quantity": item['quantity'],
                    'image': item['product'].get_product_image_url(),

                }
                for item in self.get_products()
            ]

        return package

    def pull_codes(self, merchant, quantity=1, user_id=None):
        self._cr.execute("""
            WITH pulled_codes AS (
                SELECT codes.id ,
                pt.id as product_template_id,
                pt.name as product_template_name
                FROM package_codes codes
                JOIN product_template pt on pt.id = codes.product 
                JOIN package on codes.package = %s
                    AND codes.status LIKE 'generated'
                ORDER BY RANDOM()
                LIMIT %s
                FOR UPDATE
            )
            UPDATE package_codes as codes
            SET status = 'pulled',
                pull_date = now(),
                pulled_by = %s,
                reference_user_id = %s
            FROM pulled_codes
            WHERE pulled_codes.id = codes.id
            RETURNING codes.code , codes.name, pulled_codes.product_template_id, pulled_codes.product_template_name 
        """, [self.id, quantity, merchant.id, user_id])

        pulled_codes = set(self._cr.fetchall())
        return pulled_codes

    def expiration_job(self):
        packages = self.env['package'].search(
            [('state', '=', 'published')])
        for package in packages:
            if fields.datetime.today() >= package.expiry_date:
                package.state = 'expired'
                package.action_package_expire()

    def action_package_expire(self):
        self.ensure_one()
        self._cr.execute("""
                       WITH req AS (
                           SELECT id
                             FROM redeemly_serials rs
                             LEFT JOIN package_codes pc ON rs.id = pc.serial_id 
                            WHERE state = '2'
                            and pc.package = %s 
                           FOR UPDATE
                       )
                       UPDATE redeemly_serials AS rs
                          SET state = '1',
                         FROM req
                        WHERE rs.id = req.id;
                   """, [self.id])
        self._cr.execute("""
                    WITH req AS (
                        SELECT id
                          FROM package_codes
                         WHERE status not in ('redeemed', 'expired')
                         and package = %s 
                        FOR UPDATE
                    )
                    UPDATE package_codes AS rs
                       SET status = 'expired',
                       serial_id = null,
                       expiry_date = %s

                      FROM req
                     WHERE rs.id = req.id;
                    """, [self.id, fields.datetime.today().strftime(DATETIME_FORMAT)])