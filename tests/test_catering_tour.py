from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestCateringTour(HttpCase):

    def test_catering_order_tour(self):
        self.env['res.partner'].create({'name': "Test Customer"})
        income_account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        if not income_account:
            self.env['account.account'].create({
                'name': "Test Income Account",
                'code': 'TINC',
                'account_type': 'income',
            })
        self.start_tour(
            "/odoo/action-leap_catering_management.action_catering_order",
            "leap_catering_order_tour",
            login="admin",
        )
