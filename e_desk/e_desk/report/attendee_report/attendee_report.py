# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
# from frappe.utils import today, getdate
from datetime import datetime

def execute(filters=None):
    columns = [
        {
            "fieldname": "programme",
            "fieldtype": "Data",
            "label": "Programme",
            "width": 300
        },
        {
            "fieldname": "date_time",
            "fieldtype": "Datetime",
            "label": "Date Time",
            "width": 200
        },
        {
            "fieldname": "participant_name",
            "fieldtype": "Data",
            "label": "Participant Name",
            "width": 200
        },
        {
            "fieldname": "participant",
            "fieldtype": "Link",
            "label": "Participant ID",
            "options": "Participant",
            "width": 200
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

    query = """
        SELECT
            sl.programme,
            sl.date_time,
            sl.participant_name,
            sl.participant
        FROM
            `tabScanned List` sl
        WHERE
            sl.event = %(event)s
            AND sl.programme = %(programme)s
            AND DATE(sl.date_time) = %(date_val)s
        ORDER BY sl.date_time ASC
    """

    results = frappe.db.sql(query, {
        "event": confer,
        "programme": programme,
        "date_val": formatted_date
    }, as_dict=True)

    data.extend(results)

    return columns, data




@frappe.whitelist()
def confer_agenda_list(confer, date_value):
    print(confer, "this came here....................")
    print(date_value, "dateeee...")

    # Convert string date to a datetime object and reformat
    date_value_obj = datetime.strptime(date_value, '%Y-%m-%d')
    formatted_date = date_value_obj.strftime('%Y-%m-%d')
    print(formatted_date, "this is the formatted date")

    # SQL query with correct parameter placeholders
    programmes = frappe.db.sql("""
        SELECT agenda.program_agenda
        FROM `tabConference Agenda` AS agenda
        WHERE agenda.parent = %s
        AND agenda.custom_scannable = 1
        AND DATE(agenda.start_date) = %s
    """, (confer, formatted_date), as_list=1)

    print(programmes, "query results.....................")

    # Return only the first element of each row (programme name)
    return [prog[0] for prog in programmes]


