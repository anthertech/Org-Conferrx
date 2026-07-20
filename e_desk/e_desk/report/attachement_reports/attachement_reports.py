# Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
    
     
        {
            "label": _("File Name"),
            "fieldname": "download_link",
            "fieldtype": "HTML",  # Set as HTML to render links
            "width": 300
        },
        
		{
            "label": _("Category Name"),
            "fieldname": "document_category",
            "fieldtype": "Data",
            "width": 200
        },
        
		{
            "label": _("Attachment Path"),
            "fieldname": "attachment_path",
            "fieldtype": "Data",  # Display the actual path
             "hidden":1
        },
        {
            "label": _("Conference"),
            "fieldname": "parent",
            "fieldtype": "Data",
            "width": 150,
            "hidden":1
        },
        
    ]

def get_data(filters):
    confer_id = filters.get("confer_id")
    # Use parameterized query to safely pass confer_id
    query = """
        SELECT
            parent AS parent,
            document_category AS document_category,
            -- Extract only the file name
            SUBSTRING_INDEX(attach, '/', -1) AS file_name,
            -- Create the clickable URL using the file name
            CONCAT('<a href="', attach, '" target="_blank">', SUBSTRING_INDEX(attach, '/', -1), '</a>') AS download_link
        FROM
            `tabCategory Table`
        WHERE
            parenttype = 'Conference'
            AND parent = %s
    """

    return frappe.db.sql(query, (confer_id,), as_dict=True)


@frappe.whitelist()
def get_current_confer():
    user = frappe.session.user
    conference = frappe.db.get_value(
        "Participant",
        {"user": user},
        "event",
        order_by="creation desc"
    )
    
    return conference

@frappe.whitelist()
def get_user_conferences(doctype, txt, searchfield, start, page_len, filters):
    user_email = frappe.session.user
    conference = frappe.qb.DocType("Conference")
    participant = frappe.qb.DocType("Participant")

    txt_condition = (
        conference.name.like(f"%{txt}%") | conference.title.like(f"%{txt}%")
    )

    if user_email == "Administrator" or "System Manager" in frappe.get_roles(user_email):
        conferences = (
            frappe.qb.from_(conference)
            .select(conference.name, conference.title)
            .where(txt_condition)
            .orderby(conference.name)
        )
    else:
        conferences = (
            frappe.qb.from_(conference)
            .left_join(participant)
            .on(participant.event == conference.name)
            .select(conference.name, conference.title)
            .where(
                (participant.user == user_email) 
                & txt_condition
            )
            .orderby(conference.name)
            .distinct()
        )

    return conferences.run(as_dict=False)
