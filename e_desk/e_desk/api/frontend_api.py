import frappe
from frappe import _
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 


@frappe.whitelist(allow_guest=True)
def latest_confer():
    # pass
    data=frappe.get_list('Confer', fields=['name', 'start_date', 'end_date'],filters=[['start_date', '>=', frappe.utils.nowdate()]])
    return data
import json

@frappe.whitelist(allow_guest=True)
def Getdoc(doctype):
    # Split doctype string by comma or use it as a list
    doctype_list = doctype.split(",") if isinstance(doctype, str) else doctype
    
    # Fetch and structure data for each doctype
    value = {}
    for doc in doctype_list:
        try:
            # Fetch the 'name' field for each doctype and format it
            data = frappe.db.get_all(doc, pluck='name')
            value[doc] = [{"label": item, "value": item} for item in data]
        
        except frappe.PermissionError:
            frappe.throw(f"Permission denied for doctype: {doc}")
        except Exception as e:
            frappe.log_error(f"Error fetching data for {doc}: {str(e)}", title="Doctype Fetch Error")
            frappe.throw(f"Error fetching data for {doc}")
    
    return value


@frappe.whitelist(allow_guest=True)
def submit(data):
    print(data)



@frappe.whitelist(allow_guest=True)
def ParticipantCreate(data):
  
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    mobile = data.get('mobile', '')
    email = data.get('email', '')
    chapter_value = data.get('chapter', {}).get('value', '')
    role_value = data.get('role', {}).get('value', '')
    business_value = data.get('bussines', {}).get('value', '') 
    prefix = data.get('prifix', {}).get('value', '') 
    confer_id = data.get('confer', '')
    participant_id = frappe.get_value("User", {"email": email}, "participant_id")
    print(participant_id, "participant exist..........")

    if not participant_id:

        p_doc = frappe.new_doc('Participant')
        print(email,"email",first_name,"first_name",last_name,"last_name",business_value,"business_value",role_value,"role_value",chapter_value,"chapter_value",prefix,"prefix")
        p_doc.update({
            "e_mail": email,
            "first_name": first_name,
            "last_name": last_name,
            "mobile_number": mobile,
            "business_category": business_value,
            "role": role_value,
            "chapter": chapter_value,
            "prefix": prefix,
            "full_name": f"{first_name} {last_name}",
            "event":confer_id
        })
        p_doc.save(ignore_permissions=True)
        message = f"Participant {p_doc.full_name} registered successfully for the event!"
        return {"message": message}
         
    else:

        participant_doc = frappe.get_doc("Participant", participant_id)
        participant_doc.first_name=first_name
        participant_doc.last_name=last_name
        participant_doc.full_name=f"{first_name} {last_name}"
        participant_doc.prefix=prefix
        participant_doc.role = role_value
        participant_doc.mobile_number=mobile,
        participant_doc.business_category = business_value
        participant_doc.chapter = chapter_value
        participant_doc.event=confer_id
        participant_doc.save(ignore_permissions=True)
        if confer_id:

				
            # Create an Event Participant document
            event_participant_doc = frappe.new_doc('Event Participant')
            event_participant_doc.update({
                "participant": participant_id,
                "event": confer_id,
                "event_role":"Participant",
                "business_category":business_value,
                "role":role_value ,
                "chapter":chapter_value
            })
            event_participant_doc.save(ignore_permissions=True)
    
        confer_permission_doc = frappe.new_doc('User Permission')
    
        confer_permission_doc.update({
            "user": participant_doc.e_mail,
            "allow": "Confer",
            "for_value": confer_id,
            "apply_to_all_doctypes": False, 
        })
        confer_permission_doc.save(ignore_permissions=True)

    message = f"Participant {participant_doc.full_name} registered successfully for the event!"
    return {"message": message}




        # print(p_doc,"this is the participant ....................")
 
        # qr_code = RegistrationDesk.create_qr_participant(p_doc)
        # print(qr_code,"this is qr_cde")

        # p_doc.save(ignore_permissions=True)
        # print("line 88..................")


        # doc = frappe.new_doc('User')
        # doc.update({
        #     "email": email,
        #     "first_name": first_name,
        #     "last_name": last_name,
        #     "mobile_no": mobile,
        #     "send_welcome_email": 1,
        #     "role_profile_name": "Participant",
        #     "user_type": "System User",
        #     "module_profile": "Bni profile",
        #     "participant_id": p_doc
        # })
        # print("line 102................................")

        # participant_roles = ["Participant"] 
        # for role in participant_roles:
        #     doc.append("roles", {"role": role})
        # print("107......................")
        # doc.save(ignore_permissions=True)
        # print(doc,"thisis doc")

        # if confer_id:
        #     event_participant_doc = frappe.new_doc('Event Participant')
        #     event_participant_doc.update({
        #         "participant": p_doc.name,
        #         "event": confer_id,
        #         "event_role": "Participant",
        #         "business_category": business_value,
        #         "chapter": chapter_value,
        #         "role": role_value
        #     })
        #     event_participant_doc.save(ignore_permissions=True)


        # confer_permission_doc = frappe.new_doc('User Permission')
        # confer_permission_doc.update({
        #     "user": email,
        #     "allow": "Confer",
        #     "for_value": confer_id,
        #     "apply_to_all_doctypes": False,
        # })
        # confer_permission_doc.save(ignore_permissions=True)


        # frappe.msgprint(
        #     msg=f"User created successfully!<br>Login Email: {doc.email}<br>Login Password: {self.mobile_number}",
        #     title="User Login Details",
        #     indicator='green'
        # )
    # else:
    # 		print("Coming to else case")
        
    # 		participant_doc = frappe.get_doc("Participant", participant_id)
    # 		print(participant_doc,"participant_doc")

    # 		if self.role:
    # 			participant_doc.role = self.role

    # 		if self.business_category:
    # 			participant_doc.business_category = self.business_category

    # 		if self.chapter:
    # 			participant_doc.chapter = self.chapter

    # 		participant_doc.save(ignore_permissions=True)


    # 		confer_id = self.event
    # 		if confer_id:

                
    # 			# Create an Event Participant document
    # 			event_participant_doc = frappe.new_doc('Event Participant')
    # 			event_participant_doc.update({
    # 				"participant": participant_doc.name,
    # 				"event": confer_id,
    # 				"event_role":"Participant",
    # 				"business_category":self.business_category,
    # 				"chapter":self.chapter,
    # 				"role":self.role
    # 			})
    # 			event_participant_doc.save(ignore_permissions=True)
        
    
    # 		confer_permission_doc = frappe.new_doc('User Permission')
        
    # 		confer_permission_doc.update({
    # 			"user": self.e_mail,
    # 			"allow": "Confer",
    # 			"for_value": confer_id,
    # 			"apply_to_all_doctypes": False, 
    # 		})
    # 		confer_permission_doc.save(ignore_permissions=True)

    # 		user = frappe.get_value("User", {"email": self.e_mail}, "name")
    # 		if user:
    # 			user_doc = frappe.get_doc("User", user)
    # 			user_doc.update({
    # 				"mobile_no": self.mobile_number,
    # 				"new_password": self.mobile_number
    # 			})
    # 			user_doc.save(ignore_permissions=True)
            
    # 		frappe.throw("successssssss")
            

    # 		frappe.msgprint(
    # 			msg=f"Participant details updated successfully!",
    # 			title="Update Success",
    # 			indicator='green'
    # 		)