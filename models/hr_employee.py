from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_catering_staff = fields.Boolean(
        string="Catering Staff",
        help="If checked, this employee can be assigned to catering orders.",
    )
