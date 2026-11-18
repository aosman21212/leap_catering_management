from odoo.exceptions import ValidationError
from odoo import api, fields, models


class CateringMealPackage(models.Model):
    _name = 'catering.meal.package'
    _description = 'Catering Meal Package'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    meal_type = fields.Selection([
        ('breakfast', 'Breakfast'),
        ('brunch', 'Brunch'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('buffet', 'Buffet'),
        ('snack', 'Snack / Cocktail'),
    ], default='lunch', required=True)
    menu_pdf = fields.Binary(string="Menu PDF", attachment=True)
    menu_pdf_filename = fields.Char()
    line_ids = fields.One2many('catering.meal.package.line', 'package_id', string="Food Items", copy=True)
    price_tier_ids = fields.One2many(
        'catering.meal.package.price.tier', 'package_id', string="Price Tiers", copy=True,
    )
    photo_ids = fields.Many2many(
        'catering.food.photo', 'catering_meal_package_photo_rel', 'package_id', 'photo_id',
        string="Food Photos",
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id, required=True,
    )

    def _get_price_per_head(self, guest_count):
        """Return the price per head applicable for the given guest count."""
        self.ensure_one()
        guest_count = guest_count or 0
        for tier in self.price_tier_ids.sorted('min_guests'):
            if guest_count >= tier.min_guests and (not tier.max_guests or guest_count <= tier.max_guests):
                return tier.price_per_head
        return 0.0


class CateringMealPackageLine(models.Model):
    _name = 'catering.meal.package.line'
    _description = 'Catering Meal Package Food Item'
    _order = 'package_id, sequence'

    package_id = fields.Many2one('catering.meal.package', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    food_type_id = fields.Many2one('catering.food.type', string="Course", required=True)
    food_item_id = fields.Many2one(
        'catering.food.item', string="Food Item", required=True,
        domain="[('food_type_id', '=', food_type_id)]",
    )
    note = fields.Char()

    @api.onchange('food_item_id')
    def _onchange_food_item_id(self):
        if self.food_item_id and not self.food_type_id:
            self.food_type_id = self.food_item_id.food_type_id


class CateringMealPackagePriceTier(models.Model):
    _name = 'catering.meal.package.price.tier'
    _description = 'Catering Meal Package Price Tier'
    _order = 'package_id, min_guests'

    package_id = fields.Many2one('catering.meal.package', required=True, ondelete='cascade')
    min_guests = fields.Integer(required=True, default=1)
    max_guests = fields.Integer(help="Leave empty for no upper limit.")
    price_per_head = fields.Monetary(required=True)
    currency_id = fields.Many2one(related='package_id.currency_id')

    @api.constrains('min_guests', 'max_guests')
    def _check_guests_range(self):
        for tier in self:
            if tier.min_guests < 0 or (tier.max_guests and tier.max_guests < tier.min_guests):
                raise ValidationError(
                    "The maximum number of guests must be greater than or equal to the minimum."
                )
