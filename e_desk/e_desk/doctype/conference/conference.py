# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
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
		context.agenda_list, session_speakers, mapped_speaker_ids = get_agenda_data(self)
		context.session_speakers = session_speakers

		all_speakers = get_speakers_for_event(self.name)
		context.other_speakers = [
			s for s in all_speakers if s["participant_id"] not in mapped_speaker_ids
		]

		context.registration_types = get_registration_types()
		context.has_exhibitor = has_exhibitor()
		context.connections = get_connections(self)
		context.resources = get_resources(self)
		now = frappe.utils.now_datetime()
		end_date = frappe.utils.get_datetime(self.end_date) if self.end_date else None

		context.show_e_ticket = bool(end_date and now <= end_date)
		return context


def has_exhibitor():
    has_exhibitor = frappe.db.get_value(
        "Conference",
        "event_has_exhibitors"
    )
    return has_exhibitor
    
	

def get_agenda_data(self):
	agenda = self.agenda or []
	result = []
	now = frappe.utils.now_datetime()

	# Collect unique CPA references from the agenda rows
	cpa_names = list(set(
		item.conference_programme_agenda for item in agenda
		if item.conference_programme_agenda
	))

	# Fetch all speaker rows from those CPAs in one query
	cpa_speaker_rows = {}
	if cpa_names:
		rows = frappe.get_all(
			"Speakers",
			filters={
				"parent": ["in", cpa_names],
				"parenttype": "Conference Programme Agenda",
			},
			fields=["parent", "speaker", "speaker_name"],
			order_by="idx",
		)
		for row in rows:
			cpa_speaker_rows.setdefault(row.parent, []).append(row)

	# Fetch profile photo + designation for every Participant referenced, in one query
	participant_ids = list(set(
		row.speaker for rows in cpa_speaker_rows.values() for row in rows if row.speaker
	))
	participant_map = {}
	if participant_ids:
		participants = frappe.get_all(
			"Participant",
			filters={"name": ["in", participant_ids]},
			fields=["name", "profile_photo", "custom_official_position__designation"],
		)
		participant_map = {p.name: p for p in participants}

	# session_speakers: ordered list of {"title": ..., "speakers": [...]}
	# grouped by agenda item, so the template can show the agenda name
	# first and the speakers for that session underneath it.
	session_speakers = []
	mapped_speaker_ids = set()

	for item in agenda:
		speakers_list = []
		if item.conference_programme_agenda:
			for row in cpa_speaker_rows.get(item.conference_programme_agenda, []):
				participant = participant_map.get(row.speaker)
				speakers_list.append({
					"speaker_id": row.speaker,
					"speaker_name": row.speaker_name,
					"photo": participant.profile_photo if participant else None,
					"designation": participant.custom_official_position__designation if participant else None,
				})
				if row.speaker:
					mapped_speaker_ids.add(row.speaker)

		if speakers_list and item.program_agenda:
			session_speakers.append({
				"title": item.program_agenda,
				"speakers": speakers_list,
			})

		start_date = frappe.utils.get_datetime(item.start_date) if item.start_date else None
		end_date = frappe.utils.get_datetime(item.end_date) if item.end_date else None

		is_live = False

		if start_date and end_date:
			is_live = start_date <= now <= end_date

		result.append({
			"program_agenda": item.program_agenda or "",
			"description": item.description or "",
			"start_date": item.start_date or "",
			"end_date": item.end_date or "",
			"room": item.room,
			"is_break": item.is_break,
			"speakers_list": speakers_list,
			"is_live": is_live,
		})
	return result, session_speakers, mapped_speaker_ids


def get_speakers_for_event(event_name, speaker_agenda_map=None):
    speaker_agenda_map = speaker_agenda_map or {}

    speakers = frappe.get_all(
        "Participant",
        filters={
            "event": event_name,
            "event_role": "Speaker"
        },
        fields=[
            "name",
            "full_name",
            "profile_photo",
            "custom_official_position__designation"
        ]
    )

    speaker_list = []
    for s in speakers:
        speaker_list.append({
            "full_name": s.full_name,
            "participant_id": s.name,
            "photo": s.profile_photo,
            "designation": s.custom_official_position__designation,
            "agenda_titles": speaker_agenda_map.get(s.name, []),
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


def get_connections(self):
    connections = frappe.get_all(
        "Connections",
        filters={"participant_id": frappe.session.user, "event": self.name},
        fields=["name", "participant_id", "full_name", "email", "mobile_phone", "event", "profile_photo"],
        order_by="creation desc",
    )
    participant_ids = list(set([c.email for c in connections if c.email]))
    participant_data = frappe.get_all(
        "Participant",
        filters={"user": ["in", participant_ids]},
        fields=["user", "custom_official_position__designation", "city", "country", "custom_organization__institution"],
    )
    participant_map = {
        p.user: {"designation": p.custom_official_position__designation, "city": p.city, "country": p.country, "custom_organization__institution": p.custom_organization__institution}
        for p in participant_data
    }
    for c in connections:
        info = participant_map.get(c.email, {})
        c["designation"] = info.get("designation")
        c["city"] = info.get("city")
        c["country"] = info.get("country")
        c["organization"] = info.get("custom_organization__institution")

    return connections

def get_resources(self):
    resource_rows = frappe.get_all(
        "Category Table",
        filters={
            "parent": self.name,
            "parenttype": "Conference",
            "parentfield": "attach_files",
        },
        fields=["name", "attach", "creation"],
        order_by="idx asc",
    )

    image_ext = (".png", ".jpg", ".jpeg", ".gif", ".webp")

    for r in resource_rows:
        r["file_name"] = r.attach.split("/")[-1] if r.attach else "Untitled"
        r["is_image"] = bool(r.attach) and r.attach.lower().endswith(image_ext)
        r["ext"] = r.file_name.split(".")[-1].upper() if "." in r.file_name else "FILE"
        r["uploaded_date"] = frappe.utils.formatdate(
            r.creation,
            "dd MMM yyyy"
        )

    return resource_rows


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

# class Conference(Document):

#     def before_save(self):
#         WEB_FORM_NAME = "exhibitor-registration"

#         frappe.db.set_value(
#             "Web Form",
#             WEB_FORM_NAME,
#             "published",
#             1 if self.event_has_exhibitors else 0
#         )

import frappe

@frappe.whitelist()
def get_speakers_display(cpa_name):
    if not cpa_name:
        return ""

    speakers = frappe.get_all(
        "Speakers",
        filters={
            "parent": cpa_name,
            "parenttype": "Conference Programme Agenda",
        },
        fields=["speaker_name"],
        order_by="idx",
    )

    if not speakers:
        return ""

    return "".join(f"<p>{s.speaker_name}</p>" for s in speakers)