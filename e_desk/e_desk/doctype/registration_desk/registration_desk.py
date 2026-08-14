# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate

class RegistrationDesk(Document):

    def on_trash(self):
        event_participant = frappe.get_doc(
            "Participant",
            {
                "name": self.participant_id,
            }
        )
        event_participant.is_paid = False
        event_participant.status = "Open"
        event_participant.kit_provided = "No"

        event_participant.save()
            

    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        total = 0
        for row in self.items or []:
            row.amount = flt(row.rate) * flt(row.qty)
            total += flt(row.amount)
        self.total_amount = total

    def on_submit(self):

        if not self.participant_id:
            return
        # Update Participant directly (NO save)
        frappe.db.set_value(
            "Participant",
            self.participant_id,
            {
                "status": "Registered",
                "kit_provided": self.kit_provided_
            }
        )
        frappe.msgprint("Participant registration updated successfully.")


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    """Map a submitted Registration Desk into a draft Sales Invoice (Frappe-standard mapper)."""
    def postprocess(source, target):
        target.custom_registration_desk = source.name

        # project only; currency/stock handled by company defaults / later
        if source.confer:
            target.project = frappe.db.get_value("Conference", source.confer, "project")

        if not target.company:
            target.company = frappe.defaults.get_user_default("Company")

        if target.company:
            target.flags.ignore_permissions = True
            if not target.currency:
                target.currency = frappe.db.get_value("Company", target.company, "default_currency")
            target.run_method("set_missing_values")
            target.run_method("calculate_taxes_and_totals")

    doclist = get_mapped_doc(
        "Registration Desk",
        source_name,
        {
            "Registration Desk": {
                "doctype": "Sales Invoice",
                "validation": {"docstatus": ["=", 1]},
                "field_no_map": ["naming_series", "sales_invoice"],
            },
            "Registration Desk Item": {
                "doctype": "Sales Invoice Item",
                "field_map": {
                    "item": "item_code",
                    "item_name": "item_name",
                    "qty": "qty",
                    "rate": "rate",
                },
            },
        },
        target_doc,
        postprocess,
        ignore_permissions=True,
    )

    return doclist


@frappe.whitelist()
def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
    conference = filters.get('conference')

    participants = frappe.db.sql("""
        SELECT p.name, p.full_name 
        FROM `tabParticipant` p
        WHERE p.event = %(conference)s
        AND p.name NOT IN (
            SELECT rd.participant_id
            FROM `tabRegistration Desk` rd
            WHERE rd.confer = %(conference)s
        )
        AND p.name LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
    """, {
        'conference': conference,
        'txt': "%" + txt + "%",
        'start': start,
        'page_len': page_len
    })

    return participants


@frappe.whitelist()
def registration_details(user, confer):

    # 1️⃣ Find participant for this user + event
    participant = frappe.db.get_value(
        "Participant",
        {
            "participant_id": user,
            "event": confer
        },
        ["name", "full_name", "profile_photo", "status", "customer"],
        as_dict=True
    )

    if not participant:
        frappe.throw("User is not registered for this event")

    if participant.status == "Open":
        frappe.throw("Participant is not approved yet")
    if participant.status == "Declined":
        frappe.throw("Participant Registration is Declined")

    # 2️⃣ Prevent duplicate desk registration (MAIN CHECK)
    if frappe.db.exists(
        "Registration Desk",
        {
            "participant_id": participant.name,
            "confer": confer,
            "docstatus": ["!=", 2]
        }
    ):
        frappe.throw("Participant already registered at the desk for this event")

    # 3️⃣ Get QR from User doctype
    qr = frappe.db.get_value("Participant", participant.name, "custom_qr")

    return {
        "participant_id": participant.name,
        "full_name": participant.full_name,
        "profile_photo": participant.profile_photo,
        "customer": participant.customer,
        "qr": qr
    }


@frappe.whitelist()
def get_item_price(item_code):
    """Return the latest active Item Price rate for an item (fallback to standard_rate)."""
    today = nowdate()
    prices = frappe.get_all(
        "Item Price",
        filters=[
            ["item_code", "=", item_code],
            ["valid_from", "<=", today],
        ],
        or_filters=[
            ["valid_upto", ">=", today],
            ["valid_upto", "is", "not set"],
        ],
        fields=["price_list_rate", "valid_from"],
        order_by="valid_from desc",
    )

    if prices:
        return flt(prices[0].price_list_rate)

    return flt(frappe.db.get_value("Item", item_code, "standard_rate") or 0)


