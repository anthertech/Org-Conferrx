import frappe
from frappe import _

@frappe.whitelist()
def connection_doc(scanned_user, event):
    current_user = frappe.session.user

    participant = frappe.db.get_value(
        "Participant",
        {"participant_id": scanned_user},
        ["name", "full_name", "e_mail", "mobile_number", "user", "event"],
        as_dict=True
    )

    if not participant:
        return { "status": "invalid" }

    if participant.user == current_user:
        return { "status": "same" }

    if participant.event != event:
        return { "status": "event_not_matching" }

    existing = frappe.db.exists("Connections", {
        "participant_id": current_user,
        "email": participant.e_mail
    })

    if existing:
        return {"status": "existed", "name": doc.name}
    doc = frappe.new_doc("Connections")
    doc.participant_id = current_user
    doc.full_name = participant.full_name
    doc.email = participant.e_mail
    doc.mobile_phone = participant.mobile_number
    doc.event = participant.event

    doc.insert(ignore_permissions=True)

    return {"status": "created", "name": doc.name}