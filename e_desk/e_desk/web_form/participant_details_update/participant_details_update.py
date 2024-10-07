import frappe

# def get_context(context):
# 	# do your magic here
# 	print(frappe.session.user,"ttttttttttttttttttttttttttt")
# 	print(context,"rthis is magic.......................")



def get_context(context):
    # Get the current user
    print("this is user,.........++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++...........................")
    user = frappe.session.user
    return  context
    
    # Assuming the participant is linked to the user via email or user_id
    # participant_id = frappe.db.get_value('Participant', {'user': user}, 'name')
    
    # # Assuming 'conference_id' is passed in the URL or context
    # conference_id = context.get('conference_id')
    
    # if participant_id and conference_id:
    #     # Check if the participant is registered for the conference
    #     event_participant = frappe.get_value('Event Participant', 
    #                                          {'conference': conference_id, 'participant': participant_id}, 
    #                                          'name')
    #     if event_participant:
    #         # Participant is registered, fetch their details
    #         context.participant_details = frappe.get_doc('Event Participant', event_participant)
    #     else:
    #         # Participant is not registered, set context to show an empty form
    #         context.participant_details = None
    # else:
    #     # No participant or conference ID found, set context to None
    #     context.participant_details = None
