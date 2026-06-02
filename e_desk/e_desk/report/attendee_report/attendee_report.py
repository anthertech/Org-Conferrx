# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime


def execute(filters=None):
    columns = [
        {
            "fieldname": "programme",
            "fieldtype": "Data",
            "label": "Programme",
            "width": 250
        },
        {
            "fieldname": "date_time",
            "fieldtype": "Datetime",
            "label": "Date Time",
            "width": 180
        },
        {
            "fieldname": "participant_name",
            "fieldtype": "Data",
            "label": "Participant Name",
            "width": 220
        },
        {
            "fieldname": "participant",
            "fieldtype": "Link",
            "label": "Participant ID",
            "options": "Participant",
            "width": 180
        },
        {
            "fieldname": "scanned_by",
            "fieldtype": "Link",
            "label": "Scanned By",
            "options": "User",
            "width": 220
        },
    ]

    data = []

    if not filters:
        return columns, data

    confer = filters.get("confer")
    programme = filters.get("programme")
    date_value = filters.get("date")

    if not (confer and programme and date_value):
        return columns, data

    formatted_date = datetime.strptime(date_value, "%Y-%m-%d").strftime("%Y-%m-%d")

    data = frappe.db.sql(
        """
        SELECT
            sl.programme,
            sl.date_time,
            sl.participant_name,
            sl.participant,
            sl.scanned_by
        FROM `tabScanned List` sl
        WHERE sl.event = %(event)s
          AND sl.programme = %(programme)s
          AND DATE(sl.date_time) = %(date_val)s
        ORDER BY sl.date_time ASC
        """,
        {
            "event": confer,
            "programme": programme,
            "date_val": formatted_date
        },
        as_dict=True
    )

    return columns, data


@frappe.whitelist()
def confer_agenda_list(confer, date_value):
    if not confer or not date_value:
        return []

    formatted_date = datetime.strptime(date_value, "%Y-%m-%d").strftime("%Y-%m-%d")

    programmes = frappe.db.sql(
        """
        SELECT agenda.program_agenda
        FROM `tabConference Agenda` AS agenda
        WHERE agenda.parent = %s
          AND agenda.custom_scannable = 1
          AND IFNULL(agenda.program_agenda, '') != ''
          AND DATE(agenda.start_date) <= %s
          AND DATE(agenda.end_date) >= %s
        ORDER BY agenda.start_date ASC
        """,
        (confer, formatted_date, formatted_date),
        as_list=True
    )

    return [prog[0] for prog in programmes]