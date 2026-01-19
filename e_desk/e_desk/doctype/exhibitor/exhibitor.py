# Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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

