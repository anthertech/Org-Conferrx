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
        {"label": _("Participant"), "fieldname": "full_name", "fieldtype": "Data", "width": 230},
        {"label": _("User"), "fieldname": "user", "fieldtype": "Data", "width": 230},
        {"label": _("Event"), "fieldname": "event_title", "fieldtype": "Link", "options": "Conference", "width": 400},
        {"label": _("Venue"), "fieldname": "venuelocation", "fieldtype": "Data", "width": 200},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 120},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 120},
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
            conference.title,
            conference.venuelocation,
            conference.start_date,
            conference.end_date,
        )
        .orderby(participant.full_name)
    )

    if filters.get("to_date"):
        to_date = add_to_date(get_datetime(filters.get("to_date")), days=1, seconds=-1)
        query = query.where(participant.creation <= to_date)

    if filters.get("email"):
        query = query.where(participant.user == filters["email"])
    if filters.get("event"):
        query = query.where(participant.event == filters["event"])

    rows = query.run(as_dict=True)
    if not rows:
        return []

    # group by participant (key = user/email)
    grouped = {}
    full_names = {}
    for r in rows:
        key = r.user or r.e_mail
        grouped.setdefault(key, []).append({
            "title": r.title,
            "venuelocation": r.venuelocation,
            "start_date": r.start_date,
            "end_date": r.end_date,
        })
        full_names[key] = r.full_name

    sorted_keys = sorted(grouped.keys(), key=lambda k: (full_names.get(k) or "").lower())

    data = []
    for key in sorted_keys:
        events = sorted(grouped[key], key=lambda e: e["start_date"], reverse=True)

        data.append({
            "full_name": full_names.get(key, key),
            "user": key,
            "event_title": "",
            "venuelocation": "",
            "start_date": "",
            "end_date": "",
            "indent": 0,
            "bold": 1,
        })
        for e in events:
            data.append({
                "full_name": "",
                "user": "",
                "event_title": e["title"],
                "venuelocation": e["venuelocation"],
                "start_date": e["start_date"],
                "end_date": e["end_date"],
                "indent": 1,
            })

    return data