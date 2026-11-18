from odoo import fields, models


class CateringOrderTag(models.Model):
    _name = 'catering.order.tag'
    _description = 'Catering Order Tag'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer(string="Color")

    _name_uniq = models.Constraint('UNIQUE(name)', "This tag already exists.")
