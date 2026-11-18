from odoo import fields, models


class CateringFoodType(models.Model):
    _name = 'catering.food.type'
    _description = 'Catering Food Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _name_uniq = models.Constraint(
        'UNIQUE(name)', "This food type already exists.",
    )
