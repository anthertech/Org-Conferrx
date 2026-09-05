# Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_datetime, add_to_date


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Participant"),
            "fieldname": "full_name",
            "fieldtype": "Data",
            "width": 230,
        },
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 230,
        },
        {
            "label": _("Event"),
            "fieldname": "event",
            "fieldtype": "Link",
            "options": "Conference",
            "width": 300,
        },
        {
            "label": _("Venue"),
            "fieldname": "venuelocation",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Start Date"),
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("End Date"),
            "fieldname": "end_date",
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def get_data(filters):
    participant = frappe.qb.DocType("Participant")
    conference = frappe.qb.DocType("Conference")

    query = (
        frappe.qb.from_(participant)
        .inner_join(conference)
        .on(participant.event == conference.name)
        .select(
            participant.full_name,
            participant.user,
            participant.e_mail,
            participant.creation,
            conference.name.as_("conference"),
            conference.venuelocation.as_("venuelocation"),
            conference.start_date,
            conference.end_date,
            participant.status
        )
        .orderby(participant.full_name)
    )

    if filters.get("to_date"):
        to_date = add_to_date(get_datetime(filters["to_date"]), days=1, seconds=-1)
        query = query.where(participant.creation <= to_date)

    if filters.get("email"):
        query = query.where(participant.e_mail == filters["email"])

    if filters.get("event"):
        query = query.where(participant.event == filters["event"])

    rows = query.run(as_dict=True)
    data = []

    for r in rows:
        data.append({
            "full_name": r.full_name,
            "user": r.user,
            "event": r.conference,
            "venuelocation": r.venuelocation,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "status": r.status
        })
    return data