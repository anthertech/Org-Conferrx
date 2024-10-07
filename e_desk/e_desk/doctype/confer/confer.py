# Copyright (c) 2024, sathya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Confer(Document):

	def before_save(self):
        # Create a folder for this confer if it doesn't already exist
		self.create_confer_folder()

	def  on_update(self):
		
		self.move_category_files_to_folder()
		
	def create_confer_folder(self):

		folder_name = self.title
		print(folder_name,"folder_namefolder_namefolder_name")
		
        # Check if the folder already exists
		
		existing_folder = frappe.db.exists('File', {'file_name': folder_name, 'is_folder': 1})
		print("existing_folderexisting_folderexisting_folderexisting_folder......................................................")
		
		if not existing_folder:
			
			
			new_folder = frappe.get_doc({
                "doctype": "File",
                "file_name": folder_name,
                "is_folder": 1,
                "folder": "Home", # Root folder or modify if necessary
				"is_private": 1
            })
			
			new_folder.insert()
			frappe.msgprint(f"Folder '{folder_name}' created successfully!")


	def move_category_files_to_folder(self):
		
		folder_name = self.title
		print(folder_name,"folder name.......................")
		
		folder_path = frappe.db.get_value('File', {'file_name': folder_name, 'is_folder': 1})
		print(folder_path,"folder path")
		
		if folder_path:
			for category_file in self.attach_files:
				
				if category_file.attach:
					print(category_file.attach,"category_file.attach_filescategory_file.attach_files")
					# file_doc = frappe.get_doc('File', {'file_url': category_file.attach}, 'name')
					file_list = frappe.get_list('File', filters={'file_url': category_file.attach}, fields=['name'])
					if file_list:
						# Get the latest document's name
						file_doc_name = file_list[-1].name  # Get the last document (if needed)
						
						# Now, get the actual document using the name
						file_doc = frappe.get_doc('File', file_doc_name)
					
					# file_doc = frappe.get_doc("File", category_file.attach)
					print(file_doc,"file_doc ....................this is file_doc............................")
					if file_doc.folder != folder_path:  
						file_doc.folder = folder_path	
						file_doc.save()
						frappe.msgprint(f"File '{file_doc.file_name}' moved to folder '{folder_name}'")
	




    
	