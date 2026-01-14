# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
import io
from frappe.model.document import Document
from pyqrcode import create as qr_create
# import png
import os
from frappe.model.naming import parse_naming_series
from e_desk.e_desk.utils.role import update_event_participant_role

class RegistrationDesk(Document):

    # method is for user doctype
    @classmethod
    def create_qr_participant(self, pr_doc):
        qr_image = io.BytesIO()
        data=pr_doc.name
        # data=json.dumps(data,indent=4,sort_keys=True,default=str)
        data_ = qr_create(data, error='L')
        data_.png(qr_image, scale=4, quiet_zone=1)
        name = frappe.generate_hash('', 5)
        filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
        _file = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "is_private": 0,
        "content": qr_image.getvalue(),
        "attached_to_doctype":  pr_doc.doctype,
        "attached_to_name": pr_doc.name,
        "attached_to_field":"qr"
        })
        print(pr_doc.doctype,"pr_doc.doctype",pr_doc.name,"pr_doc.name")
        # for i in frappe.get_all("File", {
        # "attached_to_doctype":  pr_doc.doctype,
        # "attached_to_name": pr_doc.name,
        # "attached_to_field":"qr"}):
        #     frappe.delete_doc("File", i.name)

        _file.save(ignore_permissions=True)
        frappe.db.set_value(pr_doc.doctype, pr_doc.name, 'qr', _file.file_url, update_modified=False)
        pr_doc.reload()
        print("line 43 .........")
        return _file.file_url


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
    qr = frappe.db.get_value("User", user, "qr")

    return {
        "participant_id": participant.name,
        "full_name": participant.full_name,
        "profile_photo": participant.profile_photo,
        "qr": qr
    }




