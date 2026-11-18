from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CateringOrder(models.Model):
    _name = 'catering.order'
    _description = 'Catering Order'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'event_date desc, id desc'

    name = fields.Char(default=lambda self: _('New'), copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True)
    event_category_id = fields.Many2one('catering.event.category', string="Event Type")
    event_date = fields.Datetime(required=True, tracking=True)
    venue = fields.Char(string="Venue")
    guest_count = fields.Integer(string="Guests", required=True, default=1, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True, copy=False)

    invoice_policy = fields.Selection([
        ('single', 'Single invoice line'),
        ('split', 'Split by package / charge'),
    ], default='single', required=True, string="Invoicing")

    package_line_ids = fields.One2many('catering.order.package.line', 'order_id', string="Meal Packages", copy=True)
    charge_line_ids = fields.One2many('catering.order.charge.line', 'order_id', string="Additional Charges", copy=True)
    staff_ids = fields.Many2many(
        'hr.employee', string="Assigned Staff", domain="[('is_catering_staff', '=', True)]",
    )
    tag_ids = fields.Many2many('catering.order.tag', string="Tags")
    photo_ids = fields.Many2many(
        'catering.food.photo', 'catering_order_photo_rel', 'order_id', 'photo_id',
        string="Food Photos",
    )

    terms_template_id = fields.Many2one('catering.terms.template', string="Terms Template")

    checklist_template_id = fields.Many2one('catering.checklist.template', string="Checklist Template")
    checklist_item_ids = fields.One2many('catering.order.checklist.item', 'order_id', string="Checklist", copy=True)
    checklist_progress = fields.Float(string="Checklist Progress", compute='_compute_checklist_progress', store=True)

    cancel_reason = fields.Text(string="Cancellation Reason", copy=False)

    attachment_count = fields.Integer(string="Order Attachment Count", compute='_compute_attachment_count')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related='company_id.currency_id')

    amount_packages = fields.Monetary(string="Packages Total", compute='_compute_amounts', store=True)
    amount_charges = fields.Monetary(string="Charges Total", compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string="Total", compute='_compute_amounts', store=True)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, copy=False)
    invoice_status = fields.Selection(
        related='invoice_id.payment_state', string="Payment Status", readonly=True,
    )

    opportunity_id = fields.Many2one('crm.lead', string="Source Lead", readonly=True, copy=False)

    rating_value = fields.Selection([
        ('1', '1 - Very Dissatisfied'),
        ('2', '2 - Dissatisfied'),
        ('3', '3 - Neutral'),
        ('4', '4 - Satisfied'),
        ('5', '5 - Very Satisfied'),
    ], string="Customer Rating", copy=False, tracking=True)
    rating_feedback = fields.Text(string="Customer Review", copy=False)
    rating_requested_on = fields.Datetime(string="Rating Requested On", readonly=True, copy=False)

    notes = fields.Text(string="Terms & Conditions")

    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = '/my/catering-orders/%s' % order.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"Catering Order - {self.name}"

    @api.depends('package_line_ids.price_subtotal', 'charge_line_ids.price_subtotal')
    def _compute_amounts(self):
        for order in self:
            order.amount_packages = sum(order.package_line_ids.mapped('price_subtotal'))
            order.amount_charges = sum(order.charge_line_ids.mapped('price_subtotal'))
            order.amount_total = order.amount_packages + order.amount_charges

    @api.depends('checklist_item_ids.state')
    def _compute_checklist_progress(self):
        for order in self:
            items = order.checklist_item_ids.filtered(lambda i: i.state != 'cancelled')
            done = items.filtered(lambda i: i.state == 'done')
            order.checklist_progress = (len(done) / len(items) * 100) if items else 0.0

    def _compute_attachment_count(self):
        attachment_data = self.env['ir.attachment']._read_group(
            [('res_model', '=', 'catering.order'), ('res_id', 'in', self.ids)],
            ['res_id'], ['__count'],
        )
        mapped_data = dict(attachment_data)
        for order in self:
            order.attachment_count = mapped_data.get(order.id, 0)

    @api.onchange('terms_template_id')
    def _onchange_terms_template_id(self):
        if self.terms_template_id:
            self.notes = self.terms_template_id.content

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('catering.order') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(_("Only draft orders can be confirmed."))
            order.state = 'confirmed'

    def action_set_draft(self):
        for order in self:
            if order.state != 'cancelled':
                raise UserError(_("Only cancelled orders can be reset to draft."))
            order.state = 'draft'

    def action_cancel(self, reason=None):
        for order in self:
            if order.state == 'invoiced':
                raise UserError(_("You cannot cancel an already invoiced order."))
            vals = {'state': 'cancelled'}
            if reason:
                vals['cancel_reason'] = reason
            order.write(vals)

    def action_done(self):
        for order in self:
            if order.state not in ('confirmed', 'invoiced'):
                raise UserError(_("Only confirmed or invoiced orders can be marked as done."))
            order.state = 'done'

    def action_send_rating_request(self):
        for order in self:
            if order.state != 'done':
                raise UserError(_("You can only request a rating once the order is done."))
            if not order.partner_id.email:
                raise UserError(_("The customer has no email address on file."))
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            rating_url = f"{base_url}{order.access_url}"
            body = Markup(
                "<p>%(greeting)s</p><p>%(intro)s</p><p><a href=\"%(url)s\">%(cta)s</a></p>"
            ) % {
                'greeting': _("Hello %(partner)s,", partner=order.partner_id.name),
                'intro': _("We hope you enjoyed your event! We would love to hear your feedback on %(order)s.", order=order.name),
                'url': rating_url,
                'cta': _("Click here to rate your experience"),
            }
            order.message_post(
                body=body,
                subject=_("How was your catering experience?"),
                partner_ids=order.partner_id.ids,
                subtype_xmlid='mail.mt_comment',
            )
            order.rating_requested_on = fields.Datetime.now()

    def action_load_checklist(self):
        for order in self:
            if not order.checklist_template_id:
                raise UserError(_("Select a checklist template first."))
            order.checklist_item_ids.unlink()
            order.checklist_item_ids = [(0, 0, {
                'name': line.name,
                'sequence': line.sequence,
            }) for line in order.checklist_template_id.line_ids]

    def action_view_opportunity(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': self.opportunity_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Attachments"),
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', 'catering.order'), ('res_id', '=', self.id)],
            'context': {'default_res_model': 'catering.order', 'default_res_id': self.id},
        }

    def _get_income_account(self):
        self.ensure_one()
        account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        if not account:
            raise UserError(_("Please configure an income account before creating an invoice."))
        return account

    def action_create_invoice(self):
        for order in self:
            if order.invoice_id:
                raise UserError(_("This order has already been invoiced."))
            if order.state != 'confirmed':
                raise UserError(_("Only confirmed orders can be invoiced."))
            if not order.package_line_ids and not order.charge_line_ids:
                raise UserError(_("Add at least one meal package or charge before invoicing."))

            account = order._get_income_account()
            invoice_lines = []
            if order.invoice_policy == 'single':
                invoice_lines.append((0, 0, {
                    'name': order.name,
                    'quantity': 1,
                    'price_unit': order.amount_total,
                    'account_id': account.id,
                }))
            else:
                for line in order.package_line_ids:
                    invoice_lines.append((0, 0, {
                        'name': _("%(package)s (%(guests)s guests)", package=line.package_id.name, guests=line.guest_count),
                        'quantity': line.guest_count,
                        'price_unit': line.unit_price,
                        'account_id': account.id,
                    }))
                for line in order.charge_line_ids:
                    invoice_lines.append((0, 0, {
                        'name': line.name,
                        'quantity': line.quantity,
                        'price_unit': line.unit_price,
                        'account_id': account.id,
                    }))

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'invoice_origin': order.name,
                'invoice_line_ids': invoice_lines,
            })
            order.invoice_id = invoice.id
            order.state = 'invoiced'
        return True

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CateringOrderPackageLine(models.Model):
    _name = 'catering.order.package.line'
    _description = 'Catering Order Meal Package Line'
    _order = 'order_id, id'

    order_id = fields.Many2one('catering.order', required=True, ondelete='cascade')
    package_id = fields.Many2one('catering.meal.package', string="Meal Package", required=True)
    guest_count = fields.Integer(string="Guests", required=True, default=1)
    unit_price = fields.Monetary(string="Price / Head")
    price_subtotal = fields.Monetary(string="Subtotal", compute='_compute_price_subtotal', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.depends('guest_count', 'unit_price')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.guest_count * line.unit_price

    @api.onchange('package_id', 'guest_count')
    def _onchange_package_id(self):
        for line in self:
            if line.package_id:
                line.unit_price = line.package_id._get_price_per_head(line.guest_count)


class CateringOrderChargeLine(models.Model):
    _name = 'catering.order.charge.line'
    _description = 'Catering Order Additional Charge Line'
    _order = 'order_id, id'

    order_id = fields.Many2one('catering.order', required=True, ondelete='cascade')
    service_charge_id = fields.Many2one('catering.service.charge', string="Service Charge")
    name = fields.Char(string="Description", required=True)
    quantity = fields.Float(default=1, required=True)
    unit_price = fields.Monetary(string="Unit Price")
    price_subtotal = fields.Monetary(string="Subtotal", compute='_compute_price_subtotal', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.depends('quantity', 'unit_price')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.unit_price

    @api.onchange('service_charge_id')
    def _onchange_service_charge_id(self):
        if self.service_charge_id:
            self.name = self.service_charge_id.name
            self.unit_price = self.service_charge_id.price
