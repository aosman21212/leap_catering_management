from odoo import fields, models


class CateringServiceCharge(models.Model):
    _name = 'catering.service.charge'
    _description = 'Catering Additional Service Charge'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    price = fields.Monetary(string="Default Price", required=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id, required=True,
    )
    active = fields.Boolean(default=True)
