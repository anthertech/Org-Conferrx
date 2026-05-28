import frappe
# abc

def execute():
	if frappe.db.exists("Custom Field", "Item-gst_hsn_code"):
		frappe.delete_doc("Custom Field", "Item-gst_hsn_code", ignore_permissions=True)
		frappe.clear_cache(doctype="Item")
