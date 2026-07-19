# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ProgrammeAttendance(Document):
    pass


@frappe.whitelist()
def process_scan(scan_qr, event, programme, docname=None):
    if not event:
        frappe.throw("Please select an Event before scanning.")

    if not programme:
        frappe.throw("Please select a Programme before scanning.")

    participant = frappe.db.get_value(
        "Participant",
        {
            "participant_id": scan_qr,
            "event": event
        },
        ["name", "full_name", "status", "meal_included"],
        as_dict=True
    )

    if not participant:
        frappe.throw("No participant found for this Event.")

    if participant.status != "Registered":
        frappe.throw(
            f"Participant is not registered. Current status: {participant.status}"
        )

    participant_name = participant.full_name or participant.name

    conference = {
        "has_meal": frappe.db.get_single_value(
            "Conference Settings",
            "has_meal"
        ),
        "meal_access": frappe.db.get_single_value(
            "Conference Settings",
            "meal_access"
        )
    }

    if conference.get("has_meal"):
        if conference.get("meal_access") != "Free for All Participants":

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
                    "Meal access denied. This participant does not have meal included."
                )

    already_scanned = frappe.db.exists(
        "Scanned List",
        {
            "participant": participant.name,
            "event": event,
            "programme": programme
        }
    )

    if already_scanned:
        frappe.throw("This participant is already scanned for this programme.")

    scanned_doc = frappe.get_doc({
        "doctype": "Scanned List",
        "participant": participant.name,
        "participant_name": participant_name,
        "event": event,
        "programme": programme,
        "date_time": now_datetime(),
        "scanned_by": frappe.session.user
    })

    scanned_doc.insert(ignore_permissions=True)

    frappe.msgprint(
        _("Scanned successfully!<br><br>"
        "<b>Participant:</b> {0}<br>"
        "<b>Event:</b> {1}<br>"
        "<b>Programme:</b> {2}").format(
            participant_name,
            event,
            programme
        ),
        title=_("Success"),
        indicator="green"
    )

    return {
        "participant_name": participant_name,
        "message": f"{participant_name} scanned successfully"
    }


@frappe.whitelist()
def get_programmes(confer):
    if not confer:
        return []

    programmes = frappe.db.sql(
        """
        SELECT agenda.program_agenda
        FROM `tabConference Agenda` AS agenda
        WHERE agenda.parent = %s
          AND agenda.custom_scannable = 1
          AND IFNULL(agenda.program_agenda, '') != ''
          AND agenda.start_date <= NOW()
          AND agenda.end_date >= NOW()
        ORDER BY agenda.start_date ASC
        """,
        (confer,),
        as_dict=True
    )

    if not programmes:
        frappe.log_error(
            message=f"No active scannable agenda found for event: {confer}",
            title="Programme Attendance"
        )

    return [row.program_agenda for row in programmes]