# Copyright (c) 2023, sathya and contributors
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
    @classmethod
    def create_qr_participant(self, pr_doc):
        qr_image = io.BytesIO()
        data={"name":pr_doc.name}
        data=json.dumps(data,indent=4,sort_keys=True,default=str)
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
    
    # Registration completed -> converting the participant status as registered
    # def on_update(self):
    #     for row in self.participant:
    #         if not row.profile_img:
    #             frappe.throw(f"Profile picture mandatory in {row.idx}")


        #     doc = frappe.get_doc("Participant", row.participant_id)
        #     # qr=self.create_qr_participant( doc)
        #     doc.status = "Registered"
        #     doc.save()
        #     # frappe.db.set_value(row.doctype, row.name, 'qr_img', qr, update_modified=False)
        # self.reload()


    # Registration canceled -> moving the particioant to old status


    def on_trash(self):
        # for row in self.participant:
            event_participant = frappe.get_doc(
            "Event Participant",
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
            
   


    # def autoname(self):
    #     if self.participant:
    #         first_item =self.participant[0]
    #         first_item_name=first_item.participant_name
    #         self.name = parse_naming_series(f"{first_item_name}-.#")




    def on_submit(self):
        # Retrieve the participant ID from the Participant Table using self.participant[0]
        # participant_data = frappe.get_value("Participant Table", self.participant[0], ["participant_id", "qr_img","name"])  
        # print(participant_data,"dataaaaaaaaaaaaaaa")
        # participant_id, qr_img,id_name = participant_data

        # profile_id=frappe.get_value("Event Participant",self.participant_id,"participant")
     
        # participant_qr=frappe.get_value("Participant",  profile_id, "qr")
        # participant_img=frappe.get_value("Participant",profile_id,"profile_photo")
        # if participant_img:
        #     frappe.db.set_value('Participant Table', id_name, 'profile_img',  participant_img)

        # #not found qrcode
        # if participant_qr:
        #     frappe.db.set_value('Participant Table', id_name, 'qr_img', participant_qr)
        # else:
        #     pr_doc = frappe.get_doc("Participant", profile_id)

        #     # Call the create_qr_participant method
        #     qr_url = RegistrationDesk.create_qr_participant(pr_doc)
        #     frappe.db.set_value('Participant Table', id_name, 'qr_img', qr_url)

    

        # Fetch the Event Participant document using the participant_id and confer
        event_participant = frappe.get_doc(
            "Event Participant",
            {
                "name": self.participant_id,
                "event": self.confer
            }
        )


        is_paid = False  
        if self.mode_of_payment:
            for payment in self.mode_of_payment:
                amount = frappe.get_value("Mode of payment", payment, "amount")
                if float(amount) > 0:
                    is_paid = True
                    break 
        # Update the Event Participant table with payment and registration status
        event_participant.is_paid = is_paid
        event_participant.reg_status = "Approved"
        event_participant.status = "Registered"
        event_participant.kit_provided=self.kit_provided_

        # Save the changes
        event_participant.save()

        # Optionally, show a confirmation message
        frappe.msgprint("Participant  registration has been updated successfully.")



@frappe.whitelist() 
def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
    conference = filters.get('conference')
    print(conference, "confere.....")
    

    participants = frappe.db.sql("""
        SELECT p.name, p.full_name 
        FROM `tabEvent Participant` p
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
def registration_details(doc,confer):

    event_participant_id = frappe.db.get_value("Event Participant", {"participant": doc, "event": confer}, "name")
    if event_participant_id:
   # Check if registration already exists in Registration Desk
        existed_registration = frappe.db.get_value("Registration Desk", {"participant_id": event_participant_id, "confer": confer}, "name")
        if existed_registration:
            frappe.throw(f"User already completed the registration. Registration ID: {existed_registration}")

        participant_details=frappe.get_doc("Participant",doc)
        participant_details_dict = participant_details.as_dict()  # Convert to dictionary
        participant_details_dict["event_participant_id"] = event_participant_id 
        print( participant_details_dict,"participant_details..............")
        return participant_details_dict
    else:
        frappe.throw("Please Register for the Event")




