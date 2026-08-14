# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
# from frappe.utils import get_timezones
from datetime import date,datetime


class Conference(WebsiteGenerator):

	def before_save(self):
        # Create a folder for this conference if it doesn't already exist
		
		if self.registration_close_date and self.end_date and  self.registration_close_date>=self.end_date:
			frappe.throw("The registration closing date cannot be greater than the event end date.")
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
						

	def get_context(self, context):
		context.agenda_list = get_agenda_data(self)
		context.speakers = get_speakers_for_event(self.name)
		context.registration_types = get_registration_types()
		context.has_exhibitor = has_exhibitor()
		context.participant = get_participant_for_event(self.name)
		return context


def has_exhibitor():
    has_exhibitor = frappe.db.get_single_value(
        "Conference Settings",
        "event_has_exhibitors"
    )
    return has_exhibitor
    
	

def get_agenda_data(self):
	agenda = self.agenda or []
	result = []

	for item in agenda:
		result.append({
			"program_agenda": item.program_agenda or "",
			"description": item.description or "",
			"start_date": item.start_date or "",
			"end_date": item.end_date or "",
		})
	return result


def get_speakers_for_event(event_name):
    speakers = frappe.get_all(
        "Participant",
        filters={
            "event": event_name,
            "event_role": "Speaker"
        },
        fields=[
            "name",
            "full_name",
            "profile_photo"
        ]
    )

    speaker_list = []
    for s in speakers:
        speaker_list.append({
            "full_name": s.full_name,
            "participant_id": s.name,
            "photo": s.profile_photo
        })

    return speaker_list



def get_registration_types():
    return frappe.get_all(
        "Item",
        fields=["name", "item_name"],
        filters={"item_group": "Registration Type"},
        order_by="item_name asc"
    )




@frappe.whitelist()
def get_confer_agenda_events(start, end):
    """Fetches the events from Conference Agenda to display in the calendar view."""

    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    has_e_desk_admin_role = 'E-Desk Admin' in user_roles

    agenda_events = []

    # ADMIN / SUPERUSER VIEW
    if user == "Administrator" or has_e_desk_admin_role:
        confer_list = frappe.get_all(
            'Conference',
            filters={
                'start_date': ['<=', end],
                'end_date': ['>=', start]
            },
            fields=['name']
        )

        for conf in confer_list:
            agenda = frappe.get_all(
                'Conference Agenda',
                filters={
                    'parent': conf.name,
                    'start_date': ['<=', end],
                    'end_date': ['>=', start]
                },
                fields=['program_agenda', 'start_date', 'end_date']
            )

            for item in agenda:
                agenda_events.append({
                    "doctype": "Conference",       # ⭐ Important
                    "name": conf.name,         # ⭐ Parent doctype ID
                    "title": item.program_agenda,
                    "start": item.start_date,
                    "end": item.end_date,
                    "color": "#FF5733"
                })

        return agenda_events

    # NORMAL USER VIEW
    participant = frappe.get_value("Participant", {"e_mail": user}, "name")
    if not participant:
        return []

    joined_confer_list = frappe.get_all(
        'Event Participant',
        filters={'participant': participant},
        fields=['event']
    )

    joined_ids = [c['event'] for c in joined_confer_list]
    if not joined_ids:
        return []

    confer_list = frappe.get_all(
        'Conference',
        filters={
            'name': ["in", joined_ids],
            'start_date': ['<=', end],
            'end_date': ['>=', start]
        },
        fields=['name']
    )

    for conf in confer_list:
        agenda = frappe.get_all(
            'Conference Agenda',
            filters={
                'parent': conf.name,
                'start_date': ['<=', end],
                'end_date': ['>=', start]
            },
            fields=['program_agenda', 'start_date', 'end_date']
        )

        for item in agenda:
            agenda_events.append({
                "doctype": "Conference",      # ⭐ Add here
                "name": conf.name,        # ⭐ Add here
                "title": item.program_agenda,
                "start": item.start_date,
                "end": item.end_date,
                "color": "#FF5733"
            })

    return agenda_events

def get_participant_for_event(event):
    if frappe.session.user == "Guest":
        return None

    participant_name = frappe.db.get_value(
        "Participant", {"event": event, "user": frappe.session.user}, "name"
    )
    if not participant_name:
        return None

    doc = frappe.get_doc("Participant", participant_name)
    meta = frappe.get_meta("Participant")

    SKIP_TYPES = {
        "Tab Break", "Section Break", "Column Break", "HTML",
        "Table", "Table MultiSelect"
    }

    SKIP_FIELDNAMES = {
        "naming_series", "participant_id", "customer", "user",
        "stall", "max_staff_allowed", "participant_address",
        "participant_contact",
        "custom_abr", "status", "custom_registration_status",
        "custom_age_category", "event_role", "event", "custom_present_paper_at_catx",
        "registration_type", "is_staff", "participant_group",
        "custom_category_files", "custom_scan_of_passports_information_page", "id_proof", "custom_scan_of_passports_information_page",
    }

    tabs = []
    current_tab = None
    current_section = None

    for f in meta.fields:
        if f.fieldtype == "Tab Break":
            current_tab = {"label": f.label or "Details", "sections": []}
            current_section = {"label": None, "fields": []}
            current_tab["sections"].append(current_section)
            tabs.append(current_tab)
            continue

        if f.fieldtype == "Section Break":
            if current_tab is None:
                current_tab = {"label": "Details", "sections": []}
                tabs.append(current_tab)
            current_section = {"label": f.label, "fields": []}
            current_tab["sections"].append(current_section)
            continue

        if f.fieldtype in SKIP_TYPES or f.fieldname in SKIP_FIELDNAMES:
            continue

        if f.hidden:
            continue

        value = doc.get(f.fieldname)
        if value in (None, "", 0) and f.fieldtype != "Check":
            continue
        if f.fieldtype == "Check" and not value:
            continue

        if f.fieldtype in ("Date",):
            value = frappe.utils.format_date(value, "dd/mm/yyyy")
        elif f.fieldtype == "Datetime":
            value = frappe.utils.format_datetime(value, "dd/mm/yyyy hh:mm a")
        elif f.fieldtype == "Check":
            value = "Yes"

        if current_tab is None:
            current_tab = {"label": "Details", "sections": []}
            current_section = {"label": None, "fields": []}
            current_tab["sections"].append(current_section)
            tabs.append(current_tab)

        current_section["fields"].append({
            "label": f.label,
            "value": value,
            "fieldtype": f.fieldtype,
            "fieldname": f.fieldname,
        })

    for t in tabs:
        t["sections"] = [s for s in t["sections"] if s["fields"]]
    tabs = [t for t in tabs if t["sections"]]

    return {
        "name": doc.name,
        "event": doc.event,
        "full_name": doc.full_name,
        "profile_photo": doc.profile_photo,
        "tabs": tabs,
    }

@frappe.whitelist(allow_guest=True)
def get_address_for_direction(address_name):
	if not address_name:
		return {}

	if not frappe.db.exists("Address", address_name):
		return {}

	address_doc = frappe.get_doc("Address", address_name)
	return {
		"address_line1": address_doc.address_line1,
		"address_line2": address_doc.address_line2,
		"city": address_doc.city,
		"state": address_doc.state,
		"pincode": address_doc.pincode,
		"country": address_doc.country,
	}
