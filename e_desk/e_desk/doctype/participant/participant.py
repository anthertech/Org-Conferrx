# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
# from frappe.core.doctype.user.user import get_roles
from frappe.utils import get_datetime, add_to_date , now ,getdate
from datetime import datetime, time, timedelta
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 
from frappe import _


class Participant(Document):
	# @frappe.whitelist(allow_guest=True)
	def after_insert(self):
		time_zone = frappe.get_value("Confer", {"is_default": 1}, "time_zone")
		if not time_zone:
			frappe.throw("PLease add Conference Time zone")
		if not self.full_name:
			self.full_name = f"{self.first_name} {self.last_name}"
			self.save(ignore_permissions=True)
		if not self.e_mail:
			frappe.throw("Email is required to create a new User.")
		if not frappe.db.exists('User',self.e_mail):
			
			doc=frappe.new_doc('User')
			doc.update({
				"email":self.e_mail,
				"time_zone":time_zone,
				"first_name":self.first_name,
				"last_name":self.last_name,
				"mobile_no":self.mobile_number,
				# "new_password":self.mobile_number,
				"send_welcome_email":1,
				"role_profile_name":"Participant",
				"user_type":"System User",
				"module_profile":"E-desk profile",
				"participant_id":self.name

			})
			roles = frappe.get_roles("Participant")
			for role in roles:
				doc.append("roles", {"role": role})
			
			doc.save(ignore_permissions=True)
			qr=RegistrationDesk.create_qr_participant(self)
			print(qr,"data coming from this..................qr")
			self.save()
			confer_id = self.event
			if confer_id:

				
				# Create an Event Participant document
				event_participant_doc = frappe.new_doc('Event Participant')
				event_participant_doc.update({
					"participant": self.name,
					"event": confer_id,
					"event_role":"Participant",
					"business_category":self.business_category,
					"role":self.role,
					"chapter":self.chapter



				})
				event_participant_doc.save(ignore_permissions=True)
        
			confer_permission_doc = frappe.new_doc('User Permission')
		
			confer_permission_doc.update({
				"user": self.e_mail,
				"allow": "Confer",
				"for_value": confer_id,
				"apply_to_all_doctypes": False, 
			})
			confer_permission_doc.save(ignore_permissions=True)
			# frappe.msgprint(
            #     msg=f"User created successfully!<br>Login Email: {doc.email}<br>Login Password: {self.mobile_number}",
            #     title="User Login Details",
            #     indicator='green'
            # )

	def validate(self):
		# Check if profile_photo is set and find related User document
		if self.profile_photo:
			# Attempt to find an existing User with this participant_id
			user = frappe.db.get_value("User", {"participant_id": self.name}, "name")
			
			# Only update if a User with this participant_id already exists
			if user:
				frappe.db.set_value("User", user, "user_image", self.profile_photo)

	@frappe.whitelist()
	def categoryfile_fetching(doc, a=None):
		category_files=frappe.get_all('Category Table', filters={'parent': 'CCA Settings'}, fields=['attach'])
		doc=frappe.get_doc(doc)
		doc.update({
			"category_files":category_files,
		})
		# doc.save()
		return category_files




	def on_trash(self):
		user_list=frappe.get_list("User",filters={"participant_id":self.name},pluck='name')
		for i in user_list:
			user=frappe.get_doc("User",i)
			user.enabled=0
			user.participant_id=''
			user.save()


	
# Converting the participant to volunteer
@frappe.whitelist()
def volunteer_creation(doc):
	doc=json.loads(doc)
	# v_doc=frappe.new_doc('Volunteer')
	# v_doc.update({
	# 	"e_mail":doc.get('e_mail'),
	# 	"mobile_number":doc.get('mobile_number'),
	# 	"name1":doc.get('full_name'),
	# 	"participant":doc.get('name'),
	# 	"module_profile":"E-desk profile",
	# }),
	# v_doc.save()

	# converting the user to volunteer profile
	user=frappe.get_doc("User",doc.get('e_mail'))
	user.update(
		{
			"role_profile_name":"Volunteer",
			"user_type":"System User"
		}
	)
	user.save()
	frappe.db.commit()



@frappe.whitelist()

def validate_food(doc):
	food_scan = frappe.db.get_single_value("CCA Settings", "food_scan_hours")

	scanned_time = ''
	buffer_hours = timedelta(hours=food_scan)
	current_time = now()

	if doc:
		doc_par = frappe.get_doc("Participant", doc)
		doc_par.append("food_scan", {
			"datetime":current_time
		})

		if len(doc_par.food_scan) >= 2:
			length = len(doc_par.food_scan)

			scanned_time = doc_par.food_scan[length - 2].datetime
			if scanned_time:
				time_difference = get_datetime(current_time) - get_datetime(scanned_time)
				if time_difference < buffer_hours:
					frappe.throw(f"Food Already Scanned at {scanned_time}")
				else:
					
					doc_par.save()
					doc_par.append("attendance_list", {
						"datetime":current_time
					})

					if len(doc_par.attendance_list) >= 2:
						length = len(doc_par.attendance_list)

						scanned_time = doc_par.attendance_list[length - 2].datetime
						if scanned_time:
							time_difference = get_datetime(current_time) - get_datetime(scanned_time)
							if time_difference < buffer_hours: 
								pass
							else:
								doc_par.save()
					else:
						doc_par.save()
		else:
			doc_par.save()
		
	return doc

@frappe.whitelist()

def validate_attendance(doc):
	attendance_scan = frappe.db.get_single_value("CCA Settings", "attendance_scan_hours")
	frappe.errprint(attendance_scan)
	scanned_time = ''
	buffer_hours = timedelta(hours=attendance_scan)
	current_time = now()

	if doc:
		doc_par = frappe.get_doc("Participant", doc)
		doc_par.append("attendance_list", {
			"datetime":current_time
		})

		if len(doc_par.attendance_list) >= 2:
			length = len(doc_par.attendance_list)

			scanned_time = doc_par.attendance_list[length - 2].datetime
			if scanned_time:
				time_difference = get_datetime(current_time) - get_datetime(scanned_time)
				if time_difference < buffer_hours:
					frappe.throw(f"Attendance Already Scanned at {scanned_time}")
				else:
					doc_par.save()
		else:
			doc_par.save()
		
	return doc
@frappe.whitelist()

def full_address(address):
	hotel=frappe.get_doc("Hotel",address)
	add=frappe.get_doc("Address",hotel.address)
	search_text = ""

	if add.address_title:
		search_text = search_text  + add.address_title
		
	if add.address_line1:
		search_text = search_text + ",<br>"+add.address_line1


	if add.city:
		search_text = search_text + ",<br>" + add.city

	if add.state:
		search_text = search_text + ",<br>" + add.state

	if add.country:
		search_text = search_text + ",<br>" + add.country

	if add.pincode:
		search_text = search_text + ",<br>" + add.pincode
	
	return search_text

@frappe.whitelist()

def full_address_church(address):
	hotel=frappe.get_doc("Church",address)
	add=frappe.get_doc("Address",hotel.address)
	search_text = ""

	if add.address_title:
		search_text = search_text  + add.address_title
		
	if add.address_line1:
		search_text = search_text + ",<br>"+add.address_line1


	if add.city:
		search_text = search_text + ",<br>" + add.city

	if add.state:
		search_text = search_text + ",<br>" + add.state

	if add.country:
		search_text = search_text + ",<br>" + add.country

	if add.pincode:
		search_text = search_text + ",<br>" + add.pincode
	
	return search_text

def atten_food_script():
	participant_lsit=frappe.get_all("Participant")
	for i in participant_lsit:
		participant=frappe.get_doc("Participant",i.name)
		if participant.food_scan:
			for j in participant.food_scan:
				food_scan_date=j.get("datetime").date()
				match=False
				for k in participant.attendance_list:
					att_scan_date=k.get("datetime").date()
					if  food_scan_date==att_scan_date:
						match=True
						break

				if match==False:
					participant.append("attendance_list", {
						"datetime":j.datetime
					})
					participant.save()
					frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def register_event_participant(email, confer_id):

	if email and confer_id:
		user = frappe.db.get_value("User", {"email": email}, "name")
		if not user:
			return "User does not exist. Please register as a new user."
		
		participant_id = frappe.db.get_value("Participant", {"e_mail": email}, "name")
		existing_registration = frappe.db.exists("Event Participant", {
			"event": confer_id,
			"participant": participant_id
		})
		
		if existing_registration:
				
			return "You are already registered for this event."
		
		
		event_participant_doc = frappe.new_doc('Event Participant')
		event_participant_doc.update({
						"participant": participant_id,
						"event": confer_id,
						"event_role":"Participant"
					})
		
		event_participant_doc.save(ignore_permissions=True)


	# code 349 sep	
		# user_permission_doc = frappe.new_doc('User Permission')
		# user_permission_doc.update({
		# 			"user": email,
		# 			"allow": "Event Participant",
		# 			"for_value": event_participant_doc.name,
		# 			"apply_to_all_doctypes": True,
		# 			# "applicable_for": ["Confer"]
		# 		})
		
		# user_permission_doc.save(ignore_permissions=True)
		  # Create User Permission for Confer doctype
		confer_permission_doc = frappe.new_doc('User Permission')
		
		confer_permission_doc.update({
            "user": email,
            "allow": "Confer",
            "for_value": confer_id,
            "apply_to_all_doctypes": False,  # Set to False if you want this permission to apply only to this specific Confer
        })
		confer_permission_doc.save(ignore_permissions=True)

		
		
		return "Registration successful!"
	else:
		return "Event is not found"



@frappe.whitelist(allow_guest=True)
def connection_doc(doc_name,email):

	user_data = frappe.get_doc("Participant", doc_name)
	print(user_data,"this is data")
	participant_id = frappe.db.get_value("Participant", {"e_mail": email}, "name")
	print(participant_id,"participant_id")
	print(email,"emailemail")
	connection_id = frappe.db.get_value("Connections", {"participant_id": participant_id, "email": user_data.e_mail}, "name")
	print(connection_id,"this is connection id..................")
	if connection_id:
		frappe.throw("This participant is already connected")

	event_id = frappe.db.get_value("Confer", {"is_default": 1}, "name")
	print(event_id,"this is even")

	if user_data:
		new_connection = frappe.new_doc('Connections')
		new_connection.update({
			"participant_id": participant_id,     
            "full_name": user_data.full_name,  # Participant who scanned the QR
            "email": user_data.e_mail, 
			"mobile_phone":user_data.mobile_number,
			"business_category":user_data.business_category,
			"profile_photo":user_data.profile_photo,
			"event":event_id
        })
		new_connection.save(ignore_permissions=True)
		return "Updated Connectionsss"

	else:
		frappe.throw("No participant found with the given QR code.")


@frappe.whitelist(allow_guest=True)
def connection_details(email):
	participant = frappe.db.get_value("Participant", {"e_mail": email}, "name")
	if not participant:
		frappe.throw("No participant found with the given email.")

	# Get all connections related to the participant
	connections = frappe.get_all("Connections", 
		filters={"participant_id": participant}, 
		fields=["full_name", "email", "mobile_phone as phone", "business_category","profile_photo","event"]
	)

	print(connections,"this is connectiosnss")
	return connections















		# Prepare the data to be displayed in HTML format
		# participant_info = f"""
		# 	<p><strong>Full Name:</strong> {user_data.full_name}</p>
		# 	<p><strong>Email:</strong> {user_data.e_mail}</p>
		# 	<p><strong>Mobile:</strong> {user_data.mobile_number}</p>
		# 	<p><strong>Business Category:</strong> {user_data.business_category}</p>
		# 	<p><strong>Chapter:</strong> {user_data.chapter}</p>
		# """
		# return participant_info

















# @frappe.whitelist(allow_guest=True)
# def testapi():
# 	print("welcomeeeeeeeeeeeeeeeeeeeeee")

# 	child_records = frappe.get_all("Confer Agenda", filters={"parentfield": ["=", ""]}, fields=["name"])

# 	for record in child_records:
# 		frappe.db.set_value("Confer Agenda", record['name'], 'parentfield', 'agenda')
# 		frappe.db.commit()

# 	frappe.msgprint(f"Updated {len(child_records)} records successfully!")




# @frappe.whitelist(allow_guest=True)
# def testapi():
# 	data = frappe.db.sql("""
#     SELECT rg.name AS registration_desk, ep.name AS participant_id, ep.full_name, pt.profile_photo
#     FROM `tabRegistration Desk` AS rg
#     JOIN `tabParticipant` AS pt
#     ON pt.old_data = rg.old_id
#     JOIN `tabEvent Participant` AS ep
#     ON ep.participant = pt.name
# 	""", as_dict=1)  # Use as_dict=1 for easier field access

# 	for item in data:
# 		# Create a new Participant Table child doctype entry
# 		doc = frappe.new_doc('Participant Table')
# 		doc.participant_id = item['participant_id']
# 		doc.participant_name = item['full_name']
# 		doc.profile_img = item['profile_photo']
# 		doc.parent = item['registration_desk']
# 		doc.parentfield = "participant"  # Ensure this is correct
# 		doc.parenttype = 'Registration Desk'

# 		# Insert the new doc (this also saves it)
# 		try:
# 			doc.insert(ignore_permissions=True)
# 			frappe.db.commit()  # Ensure the transaction is committed
# 		except Exception as e:
# 			frappe.log_error(f"Error inserting participant: {str(e)}", "Participant Insert Error")

