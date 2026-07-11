import frappe

@frappe.whitelist()
def create_event_from_project(project, data):
    data = frappe.parse_json(data)

    project_doc = frappe.get_doc("Project", project)

    # Prevent duplicate event
    existing = frappe.db.get_value(
        "Conference",
        {"project": project},
        "name"
    )
    if existing:
        frappe.throw(f"Event already exists for this project: {existing}")

    event = frappe.get_doc({
        "doctype": "Conference",
        "title": data.get("event_title"),
        "abr": data.get("abbreviation"),
        "project": project_doc.name,
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "registration_close_date": data.get("registration_close_date"),
        "time_zone": data.get("time_zone")
        })

    event.insert(ignore_permissions=True)
    frappe.db.commit()

    return event.name
