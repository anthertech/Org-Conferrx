
# import frappe
# from frappe.utils.user import is_website_user

# __version__ = '0.0.1'

# def check_app_permission():
# 	if frappe.session.user == "Administrator":
# 		return True

# 	if is_website_user():
# 		return False

# 	return True



__version__ = '0.0.1'

def check_app_permission():
    import frappe
    from frappe.utils.user import is_website_user
    if frappe.session.user == "Administrator":
        return True
    if is_website_user():
        return False
    return True