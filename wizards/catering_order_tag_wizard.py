from odoo import fields, models, _
from odoo.exceptions import UserError


class CateringOrderTagWizard(models.TransientModel):
    _name = 'catering.order.tag.wizard'
    _description = 'Bulk Update Catering Order Tags'

    order_ids = fields.Many2many(
        'catering.order', string="Orders",
        default=lambda self: self.env.context.get('active_ids'),
    )
    tag_ids = fields.Many2many('catering.order.tag', string="Tags to Add", required=True)

    def button_apply(self):
        self.ensure_one()
        if not self.order_ids:
            raise UserError(_("No orders selected."))
        for order in self.order_ids:
            order.tag_ids = [(4, tag.id) for tag in self.tag_ids]
        return {'type': 'ir.actions.act_window_close'}
