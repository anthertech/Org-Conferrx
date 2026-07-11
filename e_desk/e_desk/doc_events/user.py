import frappe
import io
import os
from pyqrcode import create as qr_create


def after_insert(doc, method=None):
    # Safety: avoid duplicate QR
    if doc.custom_qr:
        return

    # Create QR image in memory
    qr_image = io.BytesIO()
    data = doc.name  # User ID / email
    qr_obj = qr_create(data, error='L')
    qr_obj.png(qr_image, scale=4, quiet_zone=1)

    # Generate safe filename
    name = frappe.generate_hash('', 5)
    filename = f"QRCode-User-{name}.png".replace(os.path.sep, "__")

    # Create File doc
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "is_private": 0,
        "content": qr_image.getvalue(),
        "attached_to_doctype": "User",
        "attached_to_name": doc.name,
        "attached_to_field": "custom_qr",
    })

    file_doc.save(ignore_permissions=True)

    # Set QR URL in User without recursion
    frappe.db.set_value(
        "User",
        doc.name,
        "custom_qr",
        file_doc.file_url,
        update_modified=False
    )
    # Adjust user_type and roles in a safe, minimal way
    user_type_update(doc)

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
