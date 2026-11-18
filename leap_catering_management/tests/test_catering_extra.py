from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCateringExtra(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': "Extra Test Customer"})
        cls.order = cls.env['catering.order'].create({
            'partner_id': cls.partner.id,
            'event_date': '2030-01-01 18:00:00',
            'guest_count': 10,
        })

    def test_checklist_load_from_template(self):
        template = self.env['catering.checklist.template'].create({
            'name': "Standard Setup",
            'line_ids': [
                (0, 0, {'name': "Set up tables", 'sequence': 10}),
                (0, 0, {'name': "Deliver food", 'sequence': 20}),
            ],
        })
        self.order.checklist_template_id = template.id
        self.order.action_load_checklist()
        self.assertEqual(len(self.order.checklist_item_ids), 2)
        self.assertEqual(self.order.checklist_progress, 0.0)
        self.order.checklist_item_ids[0].state = 'done'
        self.assertEqual(self.order.checklist_progress, 50.0)

    def test_terms_template_fills_notes(self):
        template = self.env['catering.terms.template'].create({
            'name': "Default Terms",
            'content': "Payment due within 15 days.",
        })
        self.order.terms_template_id = template.id
        self.order._onchange_terms_template_id()
        self.assertEqual(self.order.notes, "Payment due within 15 days.")

    def test_bulk_cancel_wizard_only_cancels_draft(self):
        confirmed_order = self.env['catering.order'].create({
            'partner_id': self.partner.id,
            'event_date': '2030-01-01 18:00:00',
            'guest_count': 5,
        })
        confirmed_order.action_confirm()
        wizard = self.env['catering.order.cancel.wizard'].create({
            'order_ids': [(6, 0, (self.order | confirmed_order).ids)],
            'reason': "Client rescheduled",
        })
        wizard.button_cancel()
        self.assertEqual(self.order.state, 'cancelled')
        self.assertEqual(self.order.cancel_reason, "Client rescheduled")
        self.assertEqual(confirmed_order.state, 'confirmed')

    def test_bulk_tag_wizard(self):
        tag = self.env['catering.order.tag'].create({'name': "VIP"})
        wizard = self.env['catering.order.tag.wizard'].create({
            'order_ids': [(6, 0, self.order.ids)],
            'tag_ids': [(6, 0, tag.ids)],
        })
        wizard.button_apply()
        self.assertIn(tag, self.order.tag_ids)

    def test_crm_lead_generates_catering_order(self):
        lead = self.env['crm.lead'].create({
            'name': "Test Lead",
            'partner_id': self.partner.id,
            'catering_event_date': '2030-02-01 12:00:00',
            'catering_venue': "Test Venue",
            'catering_guest_count': 42,
        })
        action = lead.action_create_catering_order()
        order = self.env['catering.order'].browse(action['res_id'])
        self.assertEqual(order.partner_id, self.partner)
        self.assertEqual(order.venue, "Test Venue")
        self.assertEqual(order.guest_count, 42)
        self.assertEqual(lead.catering_order_id, order)
        with self.assertRaises(UserError):
            lead.action_create_catering_order()
