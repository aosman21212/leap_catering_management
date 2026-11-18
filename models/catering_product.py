from odoo import fields, models


class CateringProduct(models.Model):
    _name = 'catering.product'
    _description = 'Catering Product'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    price = fields.Monetary(string="Sales Price")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id, required=True,
    )
    active = fields.Boolean(default=True)
