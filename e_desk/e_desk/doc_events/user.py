import frappe
import io
import os
# from pyqrcode import create as qr_create



def user_type_update(doc, method=None):
    # Do not modify password or reset-related fields here.
    if not doc or not getattr(doc, 'name', None):
        return

    if frappe.flags.get('skip_user_type_update'):
        return

    # Ensure user_type is System User using targeted DB update
    if doc.user_type != "System User":
        frappe.db.set_value("User", doc.name, "user_type", "System User", update_modified=False)

    # Ensure certain roles exist; save only if roles appended
    roles_to_add = ["Customer"]
    try:
        user = frappe.get_doc("User", doc.name)
    except Exception:
        return

    added = False
    for r in roles_to_add:
        if not any(role.role == r for role in user.roles):
            user.append("roles", {"role": r})
            added = True

    if added:
        # Save minimal changes (roles). Avoid touching other fields.
        user.save(ignore_permissions=True)
        frappe.db.commit()
