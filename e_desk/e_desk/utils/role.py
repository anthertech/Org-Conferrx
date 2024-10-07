import frappe
import json

@frappe.whitelist()
def update_user_role(user, role_name):
    user.update({
        "role_profile_name": role_name,
        "user_type": "System User"
    })
    user.save()
    frappe.db.commit()


@frappe.whitelist()
def update_event_participant_role(participant,confer, role_name):
    print(participant,confer,role_name,"this are the roles...........")
    event_participant= frappe.db.get_value('Event Participant', {'event': confer,'participant':participant}, ['name'])
    frappe.db.set_value('Event Participant', event_participant, 'event_role', role_name, update_modified=False)
    user=frappe.get_doc('User',{'participant_id': participant})
    print(user.role_profile_name,"user.role_profile_name")
    user.role_profile_name = role_name
    user.save()
    frappe.db.commit()
    # update_user_role(user ,role_name)





    # deleting permissions
    user_permissions = frappe.get_all('User Permission', filters={'user': user.email}, fields=['name'])
    print(user_permissions,"this is the permissionsss",user.email)
    for i in user_permissions:
        frappe.delete_doc('User Permission', i['name'], ignore_permissions=True)


    






@frappe.whitelist()
def get_filtered_confer(doctype, txt, searchfield, start, page_len,filters):
    participant = filters.get('participant')
    # Query to get Confer records where the Event Participant has the specific participant
    # conf = frappe.db.sql(
    #     """
    #     SELECT c.name
    #     FROM `tabConfer` AS c
    #     JOIN `tabEvent Participant` AS ep ON c.name = ep.parent
    #     WHERE ep.participant = %(participant)s



    # SELECT ep.event
    #     FROM `tabEvent Participant` AS ep
    #     JOIN `tabParticipant` AS p ON p.name = ep.participant
    #     WHERE p.name = %(participant)s

    #     """,
    #     {
    #         'participant': participant
    #     }
    # )
    conf = frappe.db.sql(
        """
        SELECT ep.event
        FROM `tabEvent Participant` AS ep
        WHERE ep.participant = %(participant)s
        """,
        {
            'participant': participant
        }
    )
    
    return conf
