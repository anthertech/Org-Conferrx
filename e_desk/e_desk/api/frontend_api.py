import frappe
from frappe import _
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 
import json
from werkzeug.wrappers import Response

@frappe.whitelist(allow_guest=True)
def default_confer():
    data=frappe.get_value('Confer', {"is_default":True},['name', 'start_date', 'end_date' , "venuelocation","banner_image","registration_close_date"],as_dict=1)
    return data

@frappe.whitelist(allow_guest=True)
def Getlist(doctype):
    doctype_list = doctype.split(",") if isinstance(doctype, str) else doctype
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
def GetDoc(doctype,name):
    data = frappe.get_doc(doctype,name)
    return data

@frappe.whitelist(allow_guest=True)
def GetValue(doctype, filter, field, dict):
    filter = json.loads(filter)
    data = frappe.get_value(doctype, filter, field, as_dict=dict)
    return data

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

    # Check if the participant already exists
    participant_id = frappe.get_value("User", {"email": email}, "participant_id")
    event_participant_id = frappe.get_value("Event Participant", {"participant": participant_id, "event": confer_id})

    if event_participant_id:
        status = 403
        message = "You are already registered for this event"
        return {
            "message": message,
            "status": status
        }

    # If participant doesn't exist, create a new one
    if not participant_id:
        p_doc = frappe.new_doc('Participant')
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
            "event": confer_id
        })
        p_doc.save(ignore_permissions=True)
        message = f"Participant {p_doc.full_name} registered successfully for the event!"
        status = 200
        return {
            "message": message,
            "status": status
        }
    
    # Update participant and register for the event if needed
    else:
        participant_doc = frappe.get_doc("Participant", participant_id)
        participant_doc.update({
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "prefix": prefix,
            "role": role_value,
            "mobile_number": mobile,
            "business_category": business_value,
            "chapter": chapter_value,
            "event": confer_id
        })
        participant_doc.save(ignore_permissions=True)

        if confer_id:
            event_participant_doc = frappe.new_doc('Event Participant')
            event_participant_doc.update({
                "participant": participant_id,
                "event": confer_id,
                "event_role": "Participant",
                "business_category": business_value,
                "role": role_value,
                "chapter": chapter_value
            })
            event_participant_doc.save(ignore_permissions=True)

        message = f"Participant {participant_doc.full_name} updated and registered for the event!"
        status = 200
        return {
            "message": message,
            "status": status
        }


