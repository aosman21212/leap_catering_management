from odoo import fields, models, _
from odoo.exceptions import UserError


class CateringOrderHistoryWizard(models.TransientModel):
    _name = 'catering.order.history.wizard'
    _description = 'Print Catering Order History'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")

    def button_print(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_("The start date must be before the end date."))
        domain = [
            ('event_date', '>=', self.date_from),
            ('event_date', '<=', self.date_to),
        ]
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        orders = self.env['catering.order'].search(domain)
        if not orders:
            raise UserError(_("No orders found for the selected criteria."))
        return self.env.ref('leap_catering_management.action_report_catering_order').report_action(orders)
