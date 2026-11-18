from odoo import fields, models


class CateringChecklistTemplate(models.Model):
    _name = 'catering.checklist.template'
    _description = 'Catering Checklist Template'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('catering.checklist.template.line', 'template_id', string="Checklist Items", copy=True)


class CateringChecklistTemplateLine(models.Model):
    _name = 'catering.checklist.template.line'
    _description = 'Catering Checklist Template Line'
    _order = 'template_id, sequence'

    template_id = fields.Many2one('catering.checklist.template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)


class CateringOrderChecklistItem(models.Model):
    _name = 'catering.order.checklist.item'
    _description = 'Catering Order Checklist Item'
    _order = 'order_id, sequence'

    order_id = fields.Many2one('catering.order', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    state = fields.Selection([
        ('todo', 'To Do'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='todo', required=True)
