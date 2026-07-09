import frappe
import io
from pyqrcode import create as qr_create


def execute():
	users = frappe.get_all("User", fields=["name", "custom_qr"])
	users_to_fix = []

	for user in users:
		if not user.custom_qr:
			users_to_fix.append(user.name)
			continue

		file_name = frappe.db.get_value("File", {"file_url": user.custom_qr}, "name")
		if not file_name:
			users_to_fix.append(user.name)
			continue

		file_doc = frappe.get_doc("File", file_name)
		try:
			content = file_doc.get_content()
			if not content or len(content) == 0:
				users_to_fix.append(user.name)
		except Exception:
			users_to_fix.append(user.name)

	for email in users_to_fix:
		doc = frappe.get_doc("User", email)

		qr_image = io.BytesIO()
		qr_obj = qr_create(doc.name, error="L")
		qr_obj.png(qr_image, scale=4, quiet_zone=1)

		name_hash = frappe.generate_hash("", 5)
		filename = f"QRCode-User-{name_hash}.png"

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

		frappe.db.set_value(
			"User", doc.name, "custom_qr",
			file_doc.file_url, update_modified=False
		)

	frappe.db.commit()
	print(f"Regenerated QR codes for {len(users_to_fix)} users")