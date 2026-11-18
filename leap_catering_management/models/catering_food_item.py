from odoo import fields, models


class CateringFoodItem(models.Model):
    _name = 'catering.food.item'
    _description = 'Catering Food Item'
    _order = 'food_type_id, name'

    name = fields.Char(required=True)
    food_type_id = fields.Many2one('catering.food.type', string="Food Type", required=True, ondelete='restrict')
    description = fields.Text()
    image = fields.Image(max_width=1024, max_height=1024)
    active = fields.Boolean(default=True)
