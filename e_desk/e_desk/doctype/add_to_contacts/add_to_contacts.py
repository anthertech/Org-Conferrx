# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AddtoContacts(Document):
    def on_trash(self):
        """When Add to Contacts is deleted → delete matching Connections"""
        if not self.added_by or not self.scanned_participant:
            return

        scanned_email = frappe.db.get_value(
            "Participant",
            self.scanned_participant,
            "e_mail"
        )

        if not scanned_email:
            return

        conn = frappe.db.get_value(
            "Connections",
            {"participant_id": self.added_by, "email": scanned_email},
            "name"
        )

        if conn:
            frappe.delete_doc("Connections", conn, ignore_permissions=True)
