from odoo import fields, models


class CateringEventCategory(models.Model):
    _name = 'catering.event.category'
    _description = 'Catering Event Category'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _name_uniq = models.Constraint(
        'UNIQUE(name)', "This event category already exists.",
    )
