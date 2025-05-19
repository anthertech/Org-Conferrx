# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Church(Document):
	def after_insert(self):
		address_list=False
		if self.address:
			address=frappe.get_doc("Address",self.address)
			for i in address.links:
				if i.link_doctype=="Church" and i.link_name==self.name:
					address_list=True
			if address_list==False:
				address.update({
								'doctype':'Address',
								'links':address.links+[{"link_doctype":"Church","link_name":self.name}]
								})
				address.save(ignore_permissions=True)
