import frappe

def create_project_warehouse(doc, method=None):
    if doc.custom_warehouse:
        return

    company = doc.company or frappe.defaults.get_user_default("Company")
    if not company:
        return

    # Build warehouse name
    warehouse_name = doc.project_name

    # Check if warehouse already exists
    existing = frappe.db.get_value(
        "Warehouse",
        {"warehouse_name": warehouse_name, "company": company},
        "name"
    )

    if existing:
        doc.db_set("custom_warehouse", existing)
        return

    # Create Warehouse
    warehouse = frappe.get_doc({
        "doctype": "Warehouse",
        "warehouse_name": warehouse_name,
        "company": company,
        "is_group": 0
    })

    warehouse.insert(ignore_permissions=True)

    # Link warehouse to project
    doc.db_set("custom_warehouse", warehouse.name)
