# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConferenceSettings(Document):
        
	def before_save(self):
		WEB_FORM_NAME = "exhibitor-registration"
		frappe.db.set_value(
			"Web Form",
			WEB_FORM_NAME,
			"published",
			1 if self.event_has_exhibitors else 0
		)
		frappe.db.commit()