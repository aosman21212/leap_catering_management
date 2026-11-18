{
    'name': "Leap AI Catering Management System for Odoo | Event Catering Orders",
    'summary': "Manage meal packages, catering orders and invoicing for catering businesses",
    'description': """
Catering Management
====================
Manage your catering business end to end:

* Build reusable meal packages with per-head pricing tiers.
* Create catering orders for events (venue, date, guests, staff).
* Add additional service charges (transportation, cleaning, ...).
* Generate single or split customer invoices from an order.
""",
    'category': 'Industries',
    'version': '19.0.1.0.1',
    'license': 'LGPL-3',
    'author': "LeapAI",
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'depends': ['mail', 'hr', 'account', 'crm', 'portal'],
    'data': [
        'security/catering_security.xml',
        'security/ir.model.access.csv',
        'data/catering_sequence.xml',
        'wizards/catering_order_cancel_wizard_views.xml',
        'wizards/catering_order_tag_wizard_views.xml',
        'wizards/catering_order_history_wizard_views.xml',
        'report/catering_order_report.xml',
        'report/catering_meal_package_report.xml',
        'views/catering_food_type_views.xml',
        'views/catering_food_item_views.xml',
        'views/catering_food_photo_views.xml',
        'views/catering_event_category_views.xml',
        'views/catering_service_charge_views.xml',
        'views/catering_product_views.xml',
        'views/catering_customer_views.xml',
        'views/catering_order_tag_views.xml',
        'views/catering_terms_template_views.xml',
        'views/catering_checklist_template_views.xml',
        'views/catering_meal_package_views.xml',
        'views/catering_order_views.xml',
        'views/catering_reporting_views.xml',
        'views/catering_menus.xml',
        'views/crm_lead_views.xml',
        'views/portal_templates.xml',
    ],
    'demo': [
        'demo/catering_demo.xml',
    ],
    'assets': {
        'web.assets_tests': [
            'leap_catering_management/static/tests/tours/catering_tour.js',
        ],
    },
    'application': True,
    'installable': True,
}
