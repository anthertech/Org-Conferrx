import frappe
from datetime import date

def get_context(context):
    event_name = frappe.form_dict.get("name")

    # DETAIL PAGE
    if event_name:
        event = frappe.get_doc("Conference", event_name)
        context.event = event
        context.is_closed = date.today() > event.registration_close_date
        return context

    # LIST VIEW
    context.upcoming_events = frappe.get_all(
        "Conference",
        filters={"is_publish": 1},
        fields=["name", "title", "event_theme", "start_date", "end_date", "venuelocation","route"],
        order_by="start_date asc"
    )

    return context





