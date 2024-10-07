import frappe

def get_context(context):
	# do your magic here
	pass



@frappe.whitelist(allow_guest=True)
def check_user_exists(email):
    user = frappe.db.get_value("User", {"email": email})
    print(user,"userrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
    
    if user:
        print("coming......................")
        return user
    else:
        return None