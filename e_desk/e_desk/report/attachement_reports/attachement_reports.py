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
    # v = frappe.db.sql(query, (confer_id,), as_dict=True)
    # frappe.throw(str(v))

    return frappe.db.sql(query, (confer_id,), as_dict=True)





@frappe.whitelist()
def get_current_confer():
    print("86................................................................")
    confer_id = frappe.get_value("Conference Settings", None, "event")
    frappe.throw(str(confer_id))
    return confer_id




    # print(confer_id,"this is conferr id")
    # current_time = frappe.utils.now()  # Get the current date and time
    # current_confer = frappe.db.sql("""
    #     SELECT name FROM `tabConfer`
    #     WHERE STR_TO_DATE(start_date, '%d-%m-%Y %H:%i:%s') <= %s
    #     AND STR_TO_DATE(end_date, '%d-%m-%Y %H:%i:%s') >= %s
    #     LIMIT 1
    # """, (current_time, current_time), as_dict=True)

    # if current_confer:
    #     return current_confer[0]['name']  # Return the name of the ongoing conference
    # return None  # Return None if no ongoing conference