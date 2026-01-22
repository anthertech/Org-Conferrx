# Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from e_desk.e_desk.doctype.participant.participant import Participant


class Exhibitor(Document):
	def validate(self):
		self.validate_staff_limit()

	def validate_staff_limit(self):
		max_allowed = self.max_staff_allowed or 0
		staff_count = len(self.other_attendees or [])

		if max_allowed and staff_count > max_allowed:
			frappe.throw(
				f"Only {max_allowed} staff members are allowed for this stall. "
				f"You have added {staff_count}."
			)
	def on_submit(self):
		"""
		On submit of Exhibitor, create Participant accounts for other_attendees (staff).
		"""
		if not getattr(self, "other_attendees", None):
			return

		create_customer_enabled = getattr(self, "create_customer_for_other_attendees", 0)

		for staff in self.other_attendees:
			if not staff.email:
				continue

			# Check if Participant already exists for this email & event
			existing_participant = frappe.db.get_value(
				"Participant",
				{"e_mail": staff.email, "event": self.event},
				"name"
			)
			if existing_participant:
				continue

			# Create Participant
			participant = frappe.get_doc({
				"doctype": "Participant",
				"first_name": staff.full_name.split(" ")[0],
				"last_name": " ".join(staff.full_name.split(" ")[1:]) if len(staff.full_name.split(" ")) > 1 else "",
				"e_mail": staff.email,
				"mobile_number": staff.mobile,
				"event": self.event,
				"registration_type": "Exhibitor",
				"is_staff": 1,
				"meal_included":staff.meal_access
			})
			participant.insert(ignore_permissions=True)

			# Create User if not exists
			user = frappe.db.get_value("User", {"email": staff.email}, "name")
			if not user:
				user_doc = frappe.get_doc({
					"doctype": "User",
					"email": staff.email,
					"first_name": participant.first_name,
					"last_name": participant.last_name,
					"mobile_no": staff.mobile,
					"user_type": "System User",
					"new_password": staff.mobile,
					"send_welcome_email": 1,
					"module_profile": "E-desk profile"
				})
				if frappe.db.exists("Role", "Participant"):
					user_doc.append("roles", {"role": "Participant"})
				user_doc.save(ignore_permissions=True)
				frappe.db.commit()
				participant.db_set("user", user_doc.name)
			else:
				participant.db_set("user", user)
			
			participant.create_user_permissions()

			# Create Customer only if checkbox enabled
			if create_customer_enabled:
				participant.create_customer()

			# Create Contact for Participant
			participant.ensure_contact()
		frappe.db.commit()


# e_desk/api/webform.py

