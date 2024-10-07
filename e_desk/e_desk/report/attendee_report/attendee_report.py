# Copyright (c) 2024, sathya and contributors
# For license information, please see license.txt

import frappe


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
        
        # Fetch data based on confer and programme filters
        if confer and programme:
            # Adjust the SQL query to match your structure
            query = """
                SELECT
           
                    sl.programme AS programme,
                    sl.date_time AS date_time,
                    sl.participant_name,
                    sl.participant
                FROM
                    `tabScanned List` AS sl
 
                WHERE

                 sl.programme = %(agenda_name)s
            """
            # Fetch data
            results = frappe.db.sql(query, {
                'agenda_name': programme
            }, as_dict=True)
            data.extend(results)
        print(data)

    return columns, data




@frappe.whitelist()
def confer_agenda_list(confer):
    print(confer,"this came here....................")
    programmes = frappe.db.sql("""
        SELECT agenda.name
        FROM `tabConfer Agenda` AS agenda
        WHERE agenda.parent = %s
    """, (confer,), as_list=1)  # The closing parentheses were missing
    print(programmes,"query resultssss.....................")

    return [prog[0] for prog in programmes]  # Return only the first element of each row (programme name)

