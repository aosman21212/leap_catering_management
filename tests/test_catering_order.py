from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCateringOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': "Test Customer"})
        cls.food_type = cls.env['catering.food.type'].create({'name': "Main"})
        cls.food_item = cls.env['catering.food.item'].create({
            'name': "Test Dish",
            'food_type_id': cls.food_type.id,
        })
        cls.package = cls.env['catering.meal.package'].create({
            'name': "Test Package",
            'line_ids': [(0, 0, {
                'food_type_id': cls.food_type.id,
                'food_item_id': cls.food_item.id,
            })],
            'price_tier_ids': [
                (0, 0, {'min_guests': 1, 'max_guests': 50, 'price_per_head': 20.0}),
                (0, 0, {'min_guests': 51, 'max_guests': 0, 'price_per_head': 15.0}),
            ],
        })
        cls.service_charge = cls.env['catering.service.charge'].create({
            'name': "Transportation",
            'price': 100.0,
        })
        # Make sure there is at least one income account to invoice against.
        income_account = cls.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        if not income_account:
            cls.env['account.account'].create({
                'name': "Test Income Account",
                'code': 'TINC',
                'account_type': 'income',
            })

    def _create_order(self, guest_count=30):
        return self.env['catering.order'].create({
            'partner_id': self.partner.id,
            'event_date': '2030-01-01 18:00:00',
            'guest_count': guest_count,
            'package_line_ids': [(0, 0, {
                'package_id': self.package.id,
                'guest_count': guest_count,
                'unit_price': self.package._get_price_per_head(guest_count),
            })],
            'charge_line_ids': [(0, 0, {
                'service_charge_id': self.service_charge.id,
                'name': self.service_charge.name,
                'quantity': 1,
                'unit_price': self.service_charge.price,
            })],
        })

    def test_price_tier_lookup(self):
        self.assertEqual(self.package._get_price_per_head(10), 20.0)
        self.assertEqual(self.package._get_price_per_head(50), 20.0)
        self.assertEqual(self.package._get_price_per_head(51), 15.0)
        self.assertEqual(self.package._get_price_per_head(500), 15.0)
        self.assertEqual(self.package._get_price_per_head(0), 0.0)

    def test_order_sequence_and_amounts(self):
        order = self._create_order(guest_count=30)
        self.assertTrue(order.name and order.name != 'New')
        self.assertEqual(order.amount_packages, 30 * 20.0)
        self.assertEqual(order.amount_charges, 100.0)
        self.assertEqual(order.amount_total, 30 * 20.0 + 100.0)

    def test_confirm_required_before_invoice(self):
        order = self._create_order()
        with self.assertRaises(UserError):
            order.action_create_invoice()

    def test_single_invoice_policy(self):
        order = self._create_order(guest_count=30)
        order.invoice_policy = 'single'
        order.action_confirm()
        order.action_create_invoice()
        self.assertEqual(order.state, 'invoiced')
        self.assertTrue(order.invoice_id)
        self.assertEqual(len(order.invoice_id.invoice_line_ids), 1)
        self.assertEqual(order.invoice_id.amount_untaxed, order.amount_total)

    def test_split_invoice_policy(self):
        order = self._create_order(guest_count=30)
        order.invoice_policy = 'split'
        order.action_confirm()
        order.action_create_invoice()
        self.assertEqual(len(order.invoice_id.invoice_line_ids), 2)
        self.assertEqual(order.invoice_id.amount_untaxed, order.amount_total)

    def test_cannot_invoice_twice(self):
        order = self._create_order()
        order.action_confirm()
        order.action_create_invoice()
        with self.assertRaises(UserError):
            order.action_create_invoice()

    def test_cancel_flow(self):
        order = self._create_order()
        order.action_cancel()
        self.assertEqual(order.state, 'cancelled')
        order.action_set_draft()
        self.assertEqual(order.state, 'draft')
