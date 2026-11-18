from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    catering_event_category_id = fields.Many2one('catering.event.category', string="Event Type")
    catering_event_date = fields.Datetime(string="Event Date")
    catering_venue = fields.Char(string="Venue")
    catering_guest_count = fields.Integer(string="Guests")
    catering_order_id = fields.Many2one('catering.order', string="Catering Order", readonly=True, copy=False)

    def action_create_catering_order(self):
        self.ensure_one()
        if self.catering_order_id:
            raise UserError(_("A catering order has already been generated from this lead."))
        if not self.partner_id:
            raise UserError(_("Set a customer on the lead before generating a catering order."))
        order = self.env['catering.order'].create({
            'partner_id': self.partner_id.id,
            'event_category_id': self.catering_event_category_id.id,
            'event_date': self.catering_event_date or fields.Datetime.now(),
            'venue': self.catering_venue,
            'guest_count': self.catering_guest_count or 1,
            'opportunity_id': self.id,
        })
        self.catering_order_id = order.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'catering.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_catering_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'catering.order',
            'res_id': self.catering_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
