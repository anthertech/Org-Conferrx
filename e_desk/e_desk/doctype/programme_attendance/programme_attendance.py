# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,now_datetime


class ProgrammeAttendance(Document):
    pass

@frappe.whitelist()
def process_scan(scan_qr, event, programme, docname):

    if not event:
        frappe.throw("Please select an Event before scanning.")

    if not programme:
        frappe.throw("Please select a Programme before scanning.")

    participant = frappe.db.get_value(
        "Participant",
        {
            "user": scan_qr,
            "event": event
        },
        ["name", "full_name", "status","meal_included"],
        as_dict=True
    )

    if not participant:
        frappe.throw("No participant found for this Event.")

    if participant.status != "Registered":
        frappe.throw(
            f"Participant is not registered. Current status: {participant.status}"
        )

    conference = frappe.db.get_value(
        "Conference Settings",
        event,
        ["has_meal", "meal_access"],
        as_dict=True
    )

    if conference and conference.has_meal:
        if conference.meal_access != "Free for All Participants":

            is_meal_programme = frappe.db.get_value(
                "Conference Agenda",
                {
                    "parent": event,
                    "program_agenda": programme,
                    "meal": 1
                },
                "name"
            )

            if is_meal_programme and not participant.meal_included:
                frappe.throw(
                    "Meal access denied. This participant does not have meal included.")

    already_scanned = frappe.db.exists(
        "Scanned List",
        {
            "parent": docname,
            "participant": participant.name,
            "event": event,
            "programme": programme
        }
    )

    if already_scanned:
        frappe.throw("This participant is already scanned for this programme.")

    parent_doc = frappe.get_doc("Programme Attendance", docname)

    parent_doc.append("scanned_list", {
        "participant": participant.name,
        "participant_name": participant.full_name,
        "event": event,
        "programme": programme,
        "date_time": now_datetime()
    })

    parent_doc.save(ignore_permissions=True)
    return "Scan successful"

@frappe.whitelist()
def get_programmes(confer):
    today = nowdate()
    start_dt = f"{today} 00:00:00"
    end_dt = f"{today} 23:59:59"

    programmes = frappe.db.sql("""
        SELECT agenda.program_agenda
        FROM `tabConference Agenda` AS agenda
        WHERE agenda.parent = %s
        AND agenda.start_date BETWEEN %s AND %s
        AND agenda.custom_scannable = 1
    """, (confer, start_dt, end_dt), as_list=1)
    
    return [prog[0] for prog in programmes]
