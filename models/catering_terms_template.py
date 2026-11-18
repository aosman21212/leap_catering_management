from odoo import fields, models


class CateringTermsTemplate(models.Model):
    _name = 'catering.terms.template'
    _description = 'Catering Terms & Conditions Template'
    _order = 'name'

    name = fields.Char(required=True)
    content = fields.Text(required=True)
    active = fields.Boolean(default=True)
