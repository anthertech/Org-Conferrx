# Copyright (c) 2024, sathya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class EventParticipant(Document):
	pass


@frappe.whitelist()
def count_event():
    print("WELCOME TO THE EVENT...............................................")
    # Fetch the event value from CCA Settings
    event = frappe.db.get_single_value('Conferrx Settings', 'event')
    
    # Count the number of Event Participants linked to the fetched event
    count = frappe.db.count('Event Participant', {'event': event, 'status': 'Open'})

    # Return the count in the required format
    return {
        "value": count,
        "fieldtype": "Int",
        "route_options": {"event": event},
        "route": ["List", "Event Participant", {"event": event}]
    }


@frappe.whitelist()
def count_participant_registered():
    event = frappe.db.get_single_value('Conferrx Settings', 'event')
    
    # Count the number of Event Participants linked to the fetched event
    count = frappe.db.count('Event Participant', {'event': event, 'status': 'Registered'})

    # Return the count in the required format
    return {
        "value": count,
        "fieldtype": "Int",
        "route_options": {"event": event},
        "route": ["List", "Event Participant", {"event": event}]
    }




@frappe.whitelist()
def count_volunteer_registered():
    event = frappe.db.get_single_value('Conferrx Settings', 'event')
    
    # Count the number of Event Participants linked to the fetched event
    count = frappe.db.count('Event Participant', {'event': event, 'event_role':"Volunteer"})

    # Return the count in the required format
    return {
        "value": count,
        "fieldtype": "Int",
        "route_options": {"event": event},
        "route": ["List", "Event Participant", {"event": event}]
    }




@frappe.whitelist()
def get_confer_agenda_events(start, end):
    """Fetches the events from Confer Agenda to display in the calendar view."""

    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    print( user_roles," user_roles..........")
    has_e_desk_admin_role = 'E-Desk Admin' in user_roles

    agenda_events = []
    if user == "Administrator" or has_e_desk_admin_role:
        print("Administrator logged in, showing all events.")
        
        confer_list = frappe.get_all('Confer', filters={
            'start_date': ['<=', end],
            'end_date': ['>=', start]
        }, fields=['name'])

        for confer in confer_list:
            agenda = frappe.get_all('Confer Agenda', filters={
                'parent': confer.name,
                'start_date': ['<=', end],
                'end_date': ['>=', start]
            }, fields=['program_agenda', 'start_date', 'end_date'])

            # Add each agenda item to the calendar data with required fields
            for item in agenda:
                agenda_events.append({
                    "title": item.program_agenda,
                    "start": item.start_date,
                    "end": item.end_date,
                    "color": "#FF5733"  # Static color, you can add dynamic logic
                })
        
        return agenda_events
  
    print(user,"this is the session user")
    participant = frappe.get_value("Participant", {"e_mail": user}, "name") 
    print(participant,"id......................................")
    if not participant:
        # If the user doesn't have a participant ID, return an empty list
        return []
    
    joined_confer_list = frappe.get_all('Event Participant', filters={
        'participant': participant
    }, fields=['event']) 

    joined_confer_ids = [confer['event'] for confer in joined_confer_list]
    print(joined_confer_ids,"joined_confer_idsjoined_confer_idsjoined_confer_ids")

    if not joined_confer_ids:
        # If the user hasn't joined any events, return an empty list
        return []
    
    confer_list = frappe.get_all('Confer', filters={
        'name': ['in', joined_confer_ids],  # Only events the user joined
        'start_date': ['<=', end],
        'end_date': ['>=', start]
    }, fields=['name'])


    # Step 2: Loop through each Confer and fetch the child table data (Confer Agenda)
    for confer in confer_list:
        agenda = frappe.get_all('Confer Agenda', filters={
            'parent': confer.name,
            'start_date': ['<=', end],
            'end_date': ['>=', start]
        }, fields=['program_agenda', 'start_date', 'end_date'])
        
        # Step 3: Add each agenda item to the calendar data with required fields
        for item in agenda:
            agenda_events.append({
                "title": item.program_agenda,
                "start": item.start_date,
                "end": item.end_date,
                "color": "#FF5733"  # Example color, you can add dynamic logic for different colors
            })
    
    
    return agenda_events


# def has_permission(doc, ptype, user):
#     # Allow Volunteer to access Confer Agenda
#     print("this is the function....................................")
#     if user == "Volunteer" or "Volunteer" in frappe.get_roles(user):
#         return True
#     else:
#         return False


# def participant_query_conditions(user: str = None) -> str:
#     user = user or frappe.session.user
#     # Get the user's role profile from the User doctype
#     role_profile = frappe.db.get_value("User", {"name": user}, "role_profile_name")
#     print(role_profile,"role profile.......................")

#     # If the user is a participant or volunteer, show only their own records
#     if role_profile in ["Participant", "Volunteer"]:
#         return f"`tabParticipant`.e_mail = '{user}'"
    
#     # If the user is not a participant or volunteer, restrict access entirely
#     return None




# code 173
def event_has_permission(user: str = None) -> str:
    print("Checking permission for Conf Programme Attendee...")
    
    # Get the current user if not provided
    user = user or frappe.session.user

    # Get the user's role profile from the User doctype
    email,role_profile, participant_id = frappe.db.get_value("User", {"name": user}, ["email","role_profile_name", "participant_id"])
    print(user,participant_id,role_profile,"role profileeee..............")

    # If the user has the Participant or Volunteer role profile
    if role_profile in ["Participant"]:
        # Return the condition to restrict access to only the user's participant_id
        return f"`tabEvent Participant`.participant = '{participant_id}'"
    
    # Deny access by default
    return None



def participant_has_permission(doc, user):
    print(doc,"this si doc")
    # Get the current user if not provided
    user = user or frappe.session.user
    email,role_profile, participant_id = frappe.db.get_value("User", {"name": user}, ["email","role_profile_name", "participant_id"])
    if role_profile in ["Participant"]:
        if doc.e_mail==email:
            return True
        return False

def event_participant_has_permission(doc, user):
    print("welcomeeeeeeeeeeeeeeeeeeee")
    print(doc,"doc eventttt..............")
    user = user or frappe.session.user
    email,role_profile, participant_id = frappe.db.get_value("User", {"name": user}, ["email","role_profile_name", "participant_id"])
    print( email,role_profile, participant_id)
    if role_profile in ["Participant"]:
        if doc.participant ==participant_id:
            return True
        return False
    
# def confer_has_permission(doc, user):
#     print("welcomeeeeeeeeeeeeeeeeeeee")
#     print(doc,"doc eventttt..............")
#     user = user or frappe.session.user
#     email,role_profile, participant_id = frappe.db.get_value("User", {"name": user}, ["email","role_profile_name", "participant_id"])
#     print( email,role_profile, participant_id)
#     if role_profile in ["Participant"]:
#         event_participant_exists = frappe.db.exists("Event Participant", {
#             "participant": participant_id,  # Check for the participant ID
#             "event": doc.name  # Check if the event matches the current document
#         })
#         if event_participant_exists:
#             return True
#         return False



 
 



















# def confer_agenda_has_permission(doc, user=None, permission_type=None):
#     print("Checking permission for Confer Agenda...")
#     # Allow volunteers to access all actions (read, write, create, delete)
#     if user and "Volunteer" in frappe.get_roles(user):
#         return True
#     return False












































