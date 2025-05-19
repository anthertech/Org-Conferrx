# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
# from frappe.utils import today, getdate
from datetime import datetime

def execute(filters=None):
    columns = [
        {
            'fieldname': 'programme',
            'fieldtype': 'Link',
            'label': 'Programme',
            'options': 'Confer Agenda',
            'width': 300
        },
        {
            'fieldname': 'date_time',
            'fieldtype': 'Datetime',
            'label': 'Date_Time',
            'width': 200
        },
        {
            'fieldname': 'participant_name',
            'fieldtype': 'Data',
            'label': 'Participant Name',
            'width': 200
        },
        {
            'fieldname': 'participant',
            'fieldtype': 'Link',
            'label': 'Participant_Id',
            'options': 'Event Participant',
            'width': 200
        },
    ]
    
    data = []

    # Ensure filters are not None
    if filters:
        confer = filters.get('confer')
        programme = filters.get('programme')
        date_value = filters.get('date')
        
        # Convert date string to date object
        date_value_obj = datetime.strptime(date_value, '%Y-%m-%d')
        formatted_date = date_value_obj.strftime('%Y-%m-%d')  # Ensure date is in YYYY-MM-DD format

        print(confer, programme, f"{formatted_date} 00:00:00", "this is programme...........")

        # Fetch agenda_id from Confer Agenda
        agenda_id = frappe.db.get_value(
            "Confer Agenda",
            filters={
                "parent": confer,  
                "program_agenda": programme,  # Using the programme name dynamically
                "start_date": ["between", [f"{formatted_date} 00:00:00", f"{formatted_date} 23:59:59"]]
            },
            pluck="name"  
        )

        print(agenda_id, "agenda_id retrieved...")

        # Only proceed if an agenda_id was found
        if agenda_id:
            query = """
            SELECT
                sl.programme AS programme,
                sl.date_time AS date_time,
                sl.participant_name,
                sl.participant
            FROM
                `tabScanned List` AS sl
            WHERE
                sl.programme_id = %(agenda_id)s
                AND DATE(sl.date_time) = %(date_val)s  
            """

            # Fetch data
            results = frappe.db.sql(query, {
                'agenda_id': agenda_id,  # Pass the correct agenda_id to the query
                'date_val': formatted_date  # Use the formatted date for comparison
            }, as_dict=True)

            data.extend(results)

            print(data)

        return columns, data

    return columns, data  # Return empty data if no filters are provided






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
        FROM `tabConfer Agenda` AS agenda
        WHERE agenda.parent = %s
        AND agenda.custom_scannable = 1
        AND DATE(agenda.start_date) = %s
    """, (confer, formatted_date), as_list=1)

    print(programmes, "query results.....................")

    # Return only the first element of each row (programme name)
    return [prog[0] for prog in programmes]


