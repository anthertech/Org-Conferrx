import frappe

def get_context(context):
    print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
	# pass
# import frappe

@frappe.whitelist(allow_guest=True)
def check_user_exists(email):
    print("yes exist.................")
    print(email,"email................")
    user = frappe.db.get_value("User", {"email": email})
    
    if user:
        return user
    else:
        return None

# class Participant(Document):
#     def after_save(self):
#                 doc=frappe.db.get_doc('User',self.e_mail):
                
#                 doc.update({
#                     "send_welcome_email":0,
#                     "role_profile_name":"Participant",
#                     "roles":get_role_profile("Participant"),
#                     "user_type":"System User",
#                     "module_profile":"E-desk profile",

#                 })
#                 doc.save()
                     

