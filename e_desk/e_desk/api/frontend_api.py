import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def latest_confer():
    # pass
    data=frappe.get_list('Confer', fields=['name', 'start_date', 'end_date'],filters=[['start_date', '>=', frappe.utils.nowdate()]])
    return data
import json

@frappe.whitelist(allow_guest=True)
def Getdoc(doctype):
    # Split doctype string by comma or use it as a list
    doctype_list = doctype.split(",") if isinstance(doctype, str) else doctype
    
    # Fetch and structure data for each doctype
    value = {}
    for doc in doctype_list:
        try:
            # Fetch the 'name' field for each doctype and format it
            data = frappe.db.get_all(doc, pluck='name')
            value[doc] = [{"label": item, "value": item} for item in data]
        
        except frappe.PermissionError:
            frappe.throw(f"Permission denied for doctype: {doc}")
        except Exception as e:
            frappe.log_error(f"Error fetching data for {doc}: {str(e)}", title="Doctype Fetch Error")
            frappe.throw(f"Error fetching data for {doc}")
    
    return value


@frappe.whitelist(allow_guest=True)
def submit(data):
    print(data)