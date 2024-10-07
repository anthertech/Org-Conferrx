# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Volunteer(Document):
	# def on_trash(self):
	# 	if self.participant:
	# 		# converting the user as system user
	# 		user=frappe.get_doc("User",self.get('e_mail'))
	# 		user.update(
	# 			{
	# 				"role_profile_name":"Participant",
	# 				"user_type":"System User",
	# 				"roles":[]
	# 			}
	# 		)
	# 		user.save()
	# 		frappe.db.commit()


	def validate(self):
		if not frappe.db.exists('User',self.e_mail):
			doc=frappe.new_doc('User')


			doc.update({
				"email":self.e_mail,
				"first_name":self.name1,
				"mobile_no":self.mobile_number,
				"new_password":self.mobile_number,
				"role_profile_name":"Participant",
				"user_type":"System User",
				"send_welcome_email":0,
			}),
			doc.save()
			frappe.db.commit()
