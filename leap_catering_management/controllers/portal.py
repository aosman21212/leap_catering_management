from odoo import _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CateringCustomerPortal(CustomerPortal):

    def _get_catering_order_domain(self):
        return [('partner_id', 'child_of', [request.env.user.partner_id.commercial_partner_id.id])]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'catering_order_count' in counters:
            catering_order_model = request.env['catering.order']
            values['catering_order_count'] = (
                catering_order_model.search_count(self._get_catering_order_domain())
                if catering_order_model.check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    @route(['/my/catering-orders', '/my/catering-orders/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_catering_orders(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        CateringOrder = request.env['catering.order']

        domain = self._get_catering_order_domain()

        searchbar_sortings = {
            'date': {'label': _("Event Date"), 'order': 'event_date desc'},
            'name': {'label': _("Reference"), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _("All"), 'domain': []},
            'draft': {'label': _("Draft"), 'domain': [('state', '=', 'draft')]},
            'confirmed': {'label': _("Confirmed"), 'domain': [('state', '=', 'confirmed')]},
            'invoiced': {'label': _("Invoiced"), 'domain': [('state', '=', 'invoiced')]},
            'done': {'label': _("Done"), 'domain': [('state', '=', 'done')]},
        }
        if not filterby:
            filterby = 'all'
        domain = domain + searchbar_filters[filterby]['domain']

        if search and search_in:
            search_clauses = []
            if search_in in ('name', 'all'):
                search_clauses.append(('name', 'ilike', search))
            if search_in in ('venue', 'all'):
                search_clauses.append(('venue', 'ilike', search))
            if len(search_clauses) > 1:
                search_clauses = ['|'] * (len(search_clauses) - 1) + search_clauses
            domain += search_clauses

        order_count = CateringOrder.search_count(domain)
        pager = portal_pager(
            url="/my/catering-orders",
            url_args={'sortby': sortby, 'filterby': filterby, 'search': search, 'search_in': search_in},
            total=order_count,
            page=page,
            step=self._items_per_page,
        )
        orders = CateringOrder.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'orders': orders,
            'page_name': 'catering_order',
            'pager': pager,
            'default_url': '/my/catering-orders',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("leap_catering_management.portal_my_catering_orders", values)

    @route(['/my/catering-orders/<int:order_id>'], type='http', auth='public', website=True)
    def portal_catering_order_detail(self, order_id, access_token=None, report_type=None, download=False, **kw):
        try:
            order_sudo = self._document_check_access('catering.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=order_sudo,
                report_type=report_type,
                report_ref='leap_catering_management.action_report_catering_order',
                download=download,
            )

        values = {
            'order': order_sudo,
            'page_name': 'catering_order',
            'access_token': access_token,
        }
        return request.render("leap_catering_management.portal_catering_order_page", values)

    @route(['/my/catering-orders/<int:order_id>/rate'], type='http', auth='public', website=True, methods=['POST'])
    def portal_catering_order_rate(self, order_id, access_token=None, rating_value=None, rating_feedback=None, **kw):
        try:
            order_sudo = self._document_check_access('catering.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if rating_value in ('1', '2', '3', '4', '5'):
            order_sudo.write({
                'rating_value': rating_value,
                'rating_feedback': rating_feedback,
            })
        return request.redirect(f"/my/catering-orders/{order_sudo.id}")
