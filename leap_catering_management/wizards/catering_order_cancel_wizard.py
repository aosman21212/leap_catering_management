from odoo import fields, models, _
from odoo.exceptions import UserError


class CateringOrderCancelWizard(models.TransientModel):
    _name = 'catering.order.cancel.wizard'
    _description = 'Cancel Catering Orders'

    order_ids = fields.Many2many(
        'catering.order', string="Orders",
        default=lambda self: self.env.context.get('active_ids'),
    )
    reason = fields.Text(string="Cancellation Reason", required=True)

    def button_cancel(self):
        self.ensure_one()
        draft_orders = self.order_ids.filtered(lambda o: o.state == 'draft')
        if not draft_orders:
            raise UserError(_("None of the selected orders are in draft state."))
        draft_orders.action_cancel(reason=self.reason)
        return {'type': 'ir.actions.act_window_close'}
