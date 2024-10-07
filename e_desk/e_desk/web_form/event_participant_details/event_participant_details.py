import frappe

def get_context(context):
    pass
# 
   
# @frappe.whitelist(allow_guest=True)
# def form_update(conf):
#     print("welcomeeeee................................................................")

#     print(conf,"data comeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
 
#     user = frappe.db.get_value('User', frappe.session.user, 'participant_id')
    

#     exist = frappe.get_value('Event Participant', {'participant': user, 'parent': conf}, 'name')
    

#     conf_doc = frappe.get_doc('Confer', conf)
    

#     event_dict = {}
    
 
#     if exist:
#         event = frappe.get_doc('Event Participant', exist)
#         event_dict = event.as_dict()
#         print( event_dict," event_dict event_dict event_dict")
    

#     data = {
#         'confer': conf_doc.as_dict(), 
#         'event_dict': event_dict
#     }

#     print(data,"this is data we using......................")
    
#     return data

@frappe.whitelist(allow_guest=True)
def get_participant_id(user_email):
    print("reached the code...........")
    if user_email:
        print(user_email,"This is user got")

        # Fetch the participant ID based on the user's email
        participant = frappe.db.get_value('Participant', {'e_mail': user_email}, 'name')

        if participant:
            participant_id = participant
            print(participant_id, "participant_id.....")

            # Set the participant ID in the web form or return it
            return participant_id

    return None




@frappe.whitelist(allow_guest=True)
def check_event_participant(confer_id, user_email):
    print("this is the story")
    print(confer_id,"whjere is the conmfer")
    print(confer_id,user_email,"this is DATA ACCESSING.........................")
    # Fetch the Event Participant record based on the event and participant (user_email)
    participant = frappe.db.get_value('Participant', {'e_mail': user_email}, 'name')
    print(participant,"this is the participant we ARE USING WITH.,................................S")
    event_participant = frappe.db.get_value('Event Participant', {
        'event': confer_id,
        'participant': participant
    }, 'name')
    
    print(event_participant,"event_participantevent_participantevent_participantevent_participant")
    # If a matching record is found, return the ID
    if event_participant:
        return event_participant
    
    # If no matching record is found, return None
    return None

