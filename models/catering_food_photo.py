from odoo import fields, models


class CateringFoodPhoto(models.Model):
    _name = 'catering.food.photo'
    _description = 'Catering Food Photo'
    _order = 'name'

    name = fields.Char(required=True)
    image = fields.Image(required=True, max_width=1920, max_height=1920)
    package_ids = fields.Many2many(
        'catering.meal.package', 'catering_meal_package_photo_rel', 'photo_id', 'package_id',
        string="Used in Packages",
    )
    order_ids = fields.Many2many(
        'catering.order', 'catering_order_photo_rel', 'photo_id', 'order_id',
        string="Used in Orders",
    )
