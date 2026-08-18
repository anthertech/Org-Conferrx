# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import io
import os
import json
import frappe
from frappe import _
from pyqrcode import create as qr_create
from frappe.model.document import Document
# from frappe.core.doctype.user.user import get_roles
from datetime import datetime, time, timedelta
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 
from e_desk.e_desk.utils.password_utils import build_initial_password
from frappe.utils import cint



class Participant(Document):

	def after_insert(self):
		self.create_qr()

		if self.registration_type == "Exhibitor":
			exhibitor = frappe.get_doc({
				"doctype": "Exhibitor",
				"participant": self.name,
				"event":self.event,
				"stall": self.stall,
				"other_attendees": self.other_attendees
			})
			exhibitor.insert()

		# Find or create User
		user = frappe.db.get_value("User", {"email": self.e_mail}, "name")
		time_zone = (frappe.db.get_value("Conference", self.event, "time_zone")if self.event else None)
		print(time_zone,"ttttttttttttttttttttt")
		if user:
			user_doc = frappe.get_doc("User", user)
			# if user_doc.user_type != "System User":
				# Update the user to be a System User and fill missing details
			password = build_initial_password(self.e_mail, self.mobile_number)
			user_doc.update({
				"first_name": self.first_name or user_doc.first_name,
				"last_name": self.last_name or user_doc.last_name,
				"mobile_no": self.mobile_number or user_doc.mobile_no,
				"new_password": password,
				"time_zone": time_zone or user_doc.time_zone,
				# "send_welcome_email": 1,
				"module_profile": "E-desk profile"
			})
			if not any(role.role == "Participant" for role in user_doc.roles):
				user_doc.append("roles", {"role": "Participant"})
			user_doc.save(ignore_permissions=True)
			# frappe.db.commit()
			print("\n\n\n\nuser doc", user_doc)
		else:
			print("\n\n\n NO USERRRRRRRRRRRRRR")
			user_doc = frappe.new_doc("User")
			password = build_initial_password(self.e_mail, self.mobile_number)
			user_doc.update({
				"email": self.e_mail,
				"first_name": self.first_name,
				"last_name": self.last_name,
				"mobile_no": self.mobile_number,
				"time_zone": time_zone,
				"new_password": password,
				"send_welcome_email": 1,
				"module_profile": "E-desk profile"
			})
			if frappe.db.exists("Role", "Participant"):
				user_doc.append("roles", {"role": "Participant"})

			user_doc.insert(ignore_permissions=True)
		self.db_set("user", user_doc.name)   

		print("user created and added to participant doc....")


		# User Permission for Conference and User
		if self.event and not frappe.db.exists("User Permission", {
			"user": self.e_mail,
			"allow": "Conference",
			"for_value": self.event
		}):
			print("create_user_permissions callingggggggggggg for EVENT")
			self.create_user_permissions()
			print("user permissions too created.")

		if not self.is_staff and not self.customer and self.is_customer_creation_enabled():
			print("no customer in this participant and they are not staff")
			existing_customer = self.get_existing_customer_from_previous_participant()
			existing_customer2 = self.get_existing_customer_from_customer_portal()

			if existing_customer:
				print("prev participant has cus...........")
				self.db_set("customer", existing_customer)
			elif existing_customer2:
				print("customer portal has for this user..............")
				self.db_set("customer", existing_customer2)
			else:
				print("no where exist cus............")
				self.create_customer()
				print("cust created~~~~~~~~~~~~~~~")
		
		self.link_customer_portal_user()
		print("customer portal user linked.............")

		self.create_address_and_contact()
		print("address and contact created and linked.............")

	def on_update(self):
		if not self.user or not self.has_value_changed("event"):
			return

		time_zone = self.get_event_time_zone()
		if not time_zone:
			return

		user_doc = frappe.get_doc("User", self.user)
		if self.update_user_time_zone(user_doc, time_zone):
			user_doc.save(ignore_permissions=True)

	def validate(self):
		self.sync_contact_details()
		self.set_full_name()

	def before_insert(self):
		self.check_duplicate_registration()
		if not self.event_role:
			self.event_role = "Participant"

		if not self.participant_id:
			self.participant_id = self.generate_participant_id()

	def check_duplicate_registration(self):
		if not self.event or not self.e_mail:
			return

		existing = frappe.db.exists(
			"Participant",
			{
				"event": self.event,
				"e_mail": self.e_mail,
			}
		)

		if existing:
			frappe.throw(
				_("You have already registered for this event with the email {0}.").format(
					self.e_mail
				),
				title=_("Already Registered")
			)
	# def is_customer_creation_enabled(self):
	# # 	return frappe.db.get_value(
	# # 		"Conference",
	# # 		"create_customer_on_participant_creation"
	# # 	)
	# 	return frappe.db.get_single_value(
	# 				"Conference",
	# 				"create_customer_on_participant_creation"
	# 			)


	def is_customer_creation_enabled(self):
		if not self.event:
			return 0

		return frappe.db.get_value(
        "Conference",
        self.event,
        "create_customer_on_participant_creation"
    )


	def set_full_name(self):
		parts = [p for p in (self.first_name, self.last_name) if p]
		self.full_name = " ".join(parts)

	def link_customer_portal_user(self):
		if not self.customer or not self.user:
			return

		user_doc = frappe.get_doc("User", self.user)

		if "Customer" not in [r.role for r in user_doc.roles]:
			user_doc.append("roles", {"role": "Customer"})
			user_doc.save(ignore_permissions=True)

		customer = frappe.get_doc("Customer", self.customer)
		if not any(p.user == self.user for p in customer.portal_users):
			customer.append("portal_users", {"user": self.user})
			customer.save(ignore_permissions=True)

	def create_user_permissions(self):
		if not self.e_mail:
			return

		# 1️⃣ Conference permission
		if self.event and not frappe.db.exists("User Permission", {
			"user": self.e_mail,
			"allow": "Conference",
			"for_value": self.event
		}):
			frappe.get_doc({
				"doctype": "User Permission",
				"user": self.e_mail,
				"allow": "Conference",
				"for_value": self.event,
				"apply_to_all_doctypes": False
			}).insert(ignore_permissions=True)

		# 2️⃣ User self-permission (CRITICAL)
		if not frappe.db.exists("User Permission", {
			"user": self.e_mail,
			"allow": "User",
			"for_value": self.e_mail
		}):
			frappe.get_doc({
				"doctype": "User Permission",
				"user": self.e_mail,
				"allow": "User",
				"for_value": self.e_mail,
				"apply_to_all_doctypes": False
			}).insert(ignore_permissions=True)

	def create_address_and_contact(self):
		self.ensure_address()
		self.ensure_contact()

	def ensure_address(self):
		if self.is_staff:
			return

		address_name = frappe.db.get_value(
			"Dynamic Link",
			{
				"link_doctype": "Participant",
				"link_name": self.name,
				"parenttype": "Address",
			},
			"parent",
		)

		if not address_name:
			links = [{
				"link_doctype": "Participant",
				"link_name": self.name
			}]

			if self.customer:
				links.append({
					"link_doctype": "Customer",
					"link_name": self.customer
				})
			if self.address_title or self.address_line_1:
				address = frappe.get_doc({
					"doctype": "Address",
					"address_type": "Billing",
					"address_line1": self.address_line_1,
					"city": self.city,
					"state": self.state,
					"country": self.country,
					"pincode": self.postal_code,
					"links": links,
				})
				address.insert(ignore_permissions=True)
				address_name = address.name

		# Set primary address ONLY if customer exists
		if self.customer and not frappe.db.get_value(
			"Customer", self.customer, "customer_primary_address"
		):
			frappe.db.set_value(
				"Customer",
				self.customer,
				"customer_primary_address",
				address_name
			)

		self.db_set("participant_address", address_name)

	def ensure_contact(self):
		contact_name = frappe.db.get_value(
			"Dynamic Link",
			{
				"link_doctype": "Participant",
				"link_name": self.name,
				"parenttype": "Contact",
			},
			"parent",
		)
		
		if not contact_name:
			print("\nn\nnoooooooooooooooooooo CONNNNNNNNN\n\n\n")
			links = [{
				"link_doctype": "Participant",
				"link_name": self.name
			}]

			if self.customer:
				links.append({
					"link_doctype": "Customer",
					"link_name": self.customer
				})

			contact = frappe.get_doc({
				"doctype": "Contact",
				"first_name": self.first_name,
				"last_name": self.last_name,
				"links": links,
			})

			if self.e_mail:
				contact.append("email_ids", {
					"email_id": self.e_mail,
					"is_primary": 1
				})

			if self.mobile_number:
				contact.append("phone_nos", {
					"phone": self.mobile_number,
					"is_primary_phone": 1
				})

			contact.insert(ignore_permissions=True)
			contact_name = contact.name

		# Set primary contact ONLY if customer exists
		if self.customer and not frappe.db.get_value(
			"Customer", self.customer, "customer_primary_contact"
		):
			frappe.db.set_value(
				"Customer",
				self.customer,
				"customer_primary_contact",
				contact_name
			)

		self.db_set("participant_contact", contact_name)


	# def create_customer(self):
	# 	print("creating customer..............")
	# 	if not self.set_full_name:
	# 		self.set_full_name()

	# 	customer = frappe.get_doc({
    #     "doctype": "Customer",
    #     "customer_name": self.full_name,
    #     "customer_type": "Individual",
	# 	}).insert(ignore_permissions=True)
	# 	self.db_set("customer", customer.name)


	def create_customer(self):
			first = (self.first_name or "").strip()
			last = (self.last_name or "").strip()
			
			customer_name = f"{first} {last}".strip() if last else first

			in_import = frappe.flags.in_import
			frappe.flags.in_import = False

			try:
				customer = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_type": "Individual",
				}).insert(ignore_permissions=True)
			finally:
				frappe.flags.in_import = in_import

			self.db_set("customer", customer.name, update_modified=False)

			
	def get_existing_customer_from_previous_participant(self):
		print("checking with prev participant account")
		previous_customer = frappe.db.get_value(
			"Participant",
			{
				"e_mail": self.e_mail,
				"customer": ["!=", ""],
				"name": ["!=", self.name],
			},
			"customer",
		)
		return previous_customer
	
	def get_existing_customer_from_customer_portal(self):
		print("checking with customer portal of this user")
		existing_customer = frappe.db.get_value(
			"Portal User",  
			{"user": self.e_mail},  
			"parent"                
		)
		return existing_customer



	def sync_contact_details(self):
		print("sync_contact_details")
		if not self.participant_contact:
			return
		contact = frappe.get_doc("Contact", self.participant_contact)
		email = None
		for e in contact.email_ids:
			if e.is_primary:
				email = e.email_id
				break
		if not email and contact.email_ids:
			email = contact.email_ids[0].email_id

		phone = None
		for p in contact.phone_nos:
			if p.is_primary_phone:
				phone = p.phone
				break
		if not phone and contact.phone_nos:
			phone = contact.phone_nos[0].phone

		if email:
			self.e_mail = email
		if phone:
			self.mobile_number = phone

	def generate_participant_id(self):
		while True:
			participant_id = frappe.generate_hash(length=10).upper()

			if not frappe.db.exists(
				"Participant",
				{"participant_id": participant_id}
			):
				return participant_id

	def create_qr(self):
		if self.custom_qr:
			return

		qr_image = io.BytesIO()

		qr = qr_create(self.participant_id, error='L')
		qr.png(qr_image, scale=5, quiet_zone=1)

		filename = f"Participant-{self.e_mail}.png"

		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": filename,
			"is_private": 0,
			"content": qr_image.getvalue(),
			"attached_to_doctype": self.doctype,
			"attached_to_name": self.name,
			"attached_to_field": "custom_qr",
		})

		file_doc.save(ignore_permissions=True)

		frappe.db.set_value(
			self.doctype,
			self.name,
			"custom_qr",
			file_doc.file_url,
			update_modified=False,
		)

	

@frappe.whitelist()
def get_contact_html(contact_name):
	if not contact_name:
		return ""
	contact = frappe.get_doc("Contact", contact_name)
	email = contact.email_ids[0].email_id if contact.email_ids else ""
	phone = contact.phone_nos[0].phone if contact.phone_nos else ""
	html = f"""
		<div class="address-box" style="padding:8px;">
			<div style="display:flex; justify-content:space-between; align-items:center;">
				<strong>{contact.full_name or ""}</strong>

				<a class="btn btn-xs btn-link"
				href="/app/contact/{contact.name}"
				title="Edit Contact">
					<i class="fa fa-pencil"></i>
				</a>
			</div>

			<div>{email}</div>
			<div>{phone}</div>
		</div>
		"""
	return html

@frappe.whitelist()
def get_address_html(address_name):
	if not address_name:
		return ""
	address = frappe.get_doc("Address", address_name)
	html = f"""
	<div class="address-box" style="padding:8px;">
		<div style="display:flex; justify-content:space-between; align-items:center;">
			<strong>{address.address_title or ""}</strong>

			<a class="btn btn-xs btn-link"
			   href="/app/address/{address.name}"
			   title="Edit Address">
				<i class="fa fa-pencil"></i>
			</a>
		</div>
		<div>{address.address_line1 or ""}</div>
		{"<div>" + address.address_line2 + "</div>" if address.address_line2 else ""}
		<div>
			{address.city or ""}{" - " + address.pincode if address.pincode else ""}
		</div>
		<div>
			{address.state or ""}, {address.country or ""}
		</div>
	</div>
	"""
	return html

@frappe.whitelist()
def connection_doc(scanned_user, email):
    exists = frappe.db.exists(
        "Connections",
        {
            "participant_id": email,     
            "email": scanned_user        
        }
    )
    if exists:
        return {"status": "exists"}

    scanned = frappe.get_doc("User", scanned_user)
    conn = frappe.get_doc({
        "doctype": "Connections",
        "participant_id": email,              # ✅ scanner
        "email": scanned_user,                 # ✅ scanned
        "full_name": scanned.full_name or scanned.first_name,
        "mobile_phone": scanned.mobile_no,
        "profile_photo": scanned.user_image
    })
    conn.insert(ignore_permissions=True)
    return {"status": "created"}


@frappe.whitelist()
def connection_details(email):
    """
    Fetch all connections OWNED by this user
    """
    return frappe.get_all(
        "Connections",
        filters={"participant_id": email},
        fields=[
            "full_name",
            "email",
            "mobile_phone as phone",
            "business_category",
            "profile_photo",
            "event"
        ]
    )

@frappe.whitelist()
def toggle_event_volunteer(participant):
    if not frappe.has_permission("Participant", "write"):
        frappe.throw("Not permitted")

    participant_doc = frappe.get_doc("Participant", participant)

    if participant_doc.event_role == "Volunteer":
        new_role = "Participant"
        removing = True
    else:
        new_role = "Volunteer"
        removing = False

    participant_doc.event_role = new_role
    participant_doc.save(ignore_permissions=True)

    if not participant_doc.user:
        return

    user = frappe.get_doc("User", participant_doc.user)
    if removing:
        user.roles = [r for r in user.roles if r.role != "Volunteer"]
    else:
        if "Volunteer" not in [r.role for r in user.roles]:
            user.append("roles", {"role": "Volunteer"})
    user.save(ignore_permissions=True)


@frappe.whitelist()
def toggle_event_speaker(participant):
    if not frappe.has_permission("Participant", "write"):
        frappe.throw("Not permitted")

    participant_doc = frappe.get_doc("Participant", participant)

    # Toggle logic
    if participant_doc.event_role == "Speaker":
        participant_doc.event_role = "Participant"
    else:
        participant_doc.event_role = "Speaker"

    participant_doc.save(ignore_permissions=True)



@frappe.whitelist(allow_guest=True)
def get_meal_settings():
	settings = frappe.get_doc("Conference")
	return {
		"has_meal": settings.has_meal,
		"meal_access": settings.meal_access
	}

@frappe.whitelist(allow_guest=True)
def get_meal_settings_for_webform(event):

    if not event:
        return {
            "has_meal": 0,
            "meal_access": None,
        }

    settings = frappe.get_doc("Conference", event)

    return {
        "has_meal": settings.has_meal,
        "meal_access": settings.meal_access,
    }





BREAK_FIELDTYPES = ("Section Break", "Column Break", "Page Break")
SECTION_ENDS = ("Section Break", "Page Break")

@frappe.whitelist(allow_guest=True)
def get_registration_configuration(conference):
		if not conference or not frappe.db.exists("Conference", conference):
			return {}

		# 1. Fetch all fields for the Web Form
		webform_fields = frappe.get_all(
			"Web Form Field",
			filters={"parent": "event-participant-registration"},
			fields=["fieldname", "fieldtype"],
			order_by="idx asc",
		)

		# 2. Find which Conference meta fields are Checkboxes
		conference_meta = frappe.get_meta("Conference")
		conference_checkbox_fields = {
			df.fieldname for df in conference_meta.fields if df.fieldtype == "Check"
		}
		# print(conference_checkbox_fields,"conference_checkbox_fields")
		# 3. Filter leaf fields that match your criteria
		leaf_fieldnames = [
			df.fieldname
			for df in webform_fields
			if df.fieldname
			and df.fieldtype not in BREAK_FIELDTYPES
			and df.fieldname in conference_checkbox_fields
		]
		# print(leaf_fieldnames ,"leaf_fieldnames ")
		
		# 4. FIXED: Fetch safely using a clean list format
		conference_values = {}
		if leaf_fieldnames:
			db_values = frappe.db.get_value(
				"Conference",
				conference,
				leaf_fieldnames,  # Pass list directly
				as_dict=True
			)
			if db_values:
				conference_values = db_values


		# 5. Populate initial configuration dictionary
		config = {}
		total = len(webform_fields)
	
		# Add only enabled fields
		for fieldname in leaf_fieldnames:
			if cint(conference_values.get(fieldname, 0)) == 1:
				config[fieldname] = 1

		# Add only visible sections/pages
		for i, field in enumerate(webform_fields):
			if field.fieldtype not in BREAK_FIELDTYPES or not field.fieldname:
				continue

			keep_visible = False

			for j in range(i + 1, total):
				nxt = webform_fields[j]

				if nxt.fieldtype == "Column Break":
					continue

				if nxt.fieldtype in SECTION_ENDS:
					break

				if nxt.fieldname in config:
					keep_visible = True
					break

			if keep_visible:
				config[field.fieldname] = 1
		return config

@frappe.whitelist(allow_guest=True)
def get_conference_descriptions_for_webform(event):
    if not event or not frappe.db.exists("Conference", event):
        return {}

    data = frappe.db.get_value(
        "Conference",
        event,
        [
            "accomodation_description",
            "travel_description",
            "deliberative_session_description",
        ],
        as_dict=True,
    )
    return data or {}

