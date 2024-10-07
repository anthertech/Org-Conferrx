# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CategoryName(Document):
	#new adding also updaing in the participant - category files
    pass

	# def on_update(self):
	# 	self.capacity_file_url
	# 	category_files=frappe.get_all('Participant', filters={'capacity': self.name}, fields=['name'])

	# 	for i in category_files:
	# 		category_doc=frappe.get_doc("Participant",i["name"])
	# 		for j in self.capacity_file_url:
	# 			category_doc.append(
   	# 			"category_files",
	# 			{
    #                "attach":j.attach
    #             },
	# 		  )
	# 			category_doc.save()	
	# 	file_list=[]

	# 	for k in self.capacity_file_url:	
	# 		file_list.append(k.attach)

	# 	file_list=frappe.get_all('File',filters={"attached_to_doctype":self.doctype,"attached_to_name":self.name, "file_url":["not in",file_list]})
	# 	for file in file_list:
	# 		frappe.delete_doc("File", file.name)
