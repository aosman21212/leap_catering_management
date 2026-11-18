import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("leap_catering_order_tour", {
    url: "/odoo/action-leap_catering_management.action_catering_order",
    steps: () => [
        {
            trigger: ".o_list_button_add",
            content: "Create a new catering order",
            run: "click",
        },
        {
            trigger: "div[name='partner_id'] input",
            content: "Set the customer",
            run: "edit Test Customer",
        },
        {
            trigger: ".o-autocomplete--dropdown-item:contains('Test Customer')",
            run: "click",
        },
        {
            trigger: "div[name='event_date'] input",
            content: "Set the event date",
            run: "edit 12/31/2030 18:00:00",
        },
        {
            trigger: "div[name='guest_count'] input",
            content: "Set the number of guests",
            run: "edit 25",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save the order",
            run: "click",
        },
        {
            trigger: ".o_form_saved, .o_breadcrumb",
            content: "Order saved",
        },
    ],
});
