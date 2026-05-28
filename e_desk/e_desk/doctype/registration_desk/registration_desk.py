# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
import io
from frappe.model.document import Document
from pyqrcode import create as qr_create
# import png
import os

class RegistrationDesk(Document):

    def on_trash(self):
        # for row in self.participant:
            event_participant = frappe.get_doc(
            "Participant",
            {
                "name": self.participant_id,
            }
            )
            event_participant.is_paid = False
            # event_participant.reg_status = "Pending"
            event_participant.status = "Open"
            event_participant.kit_provided="No"

            # Save the changes
            event_participant.save()
            

    def on_submit(self):

        if not self.participant_id:
            return
        # Check payment
        is_paid = False
        for payment in self.mode_of_payment or []:
            if payment.amount and float(payment.amount) > 0:
                is_paid = True
                break
        # Update Participant directly (NO save)
        frappe.db.set_value(
            "Participant",
            self.participant_id,
            {
                "is_paid": is_paid,
                "status": "Registered",
                "kit_provided": self.kit_provided_
            }
        )
        frappe.msgprint("Participant registration updated successfully.")



@frappe.whitelist() 
def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
    conference = filters.get('conference')
    print(conference, "confere.....")
    

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
            "user": user,
            "event": confer
        },
        ["name", "full_name", "profile_photo", "status"],
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
    qr = frappe.db.get_value("User", user, "custom_qr")

    return {
        "participant_id": participant.name,
        "full_name": participant.full_name,
        "profile_photo": participant.profile_photo,
        "qr": qr
    }




