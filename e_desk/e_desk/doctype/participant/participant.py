# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
# from frappe.core.doctype.user.user import get_roles
from datetime import datetime, time, timedelta
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 


class Participant(Document):

	def after_insert(self):
		if self.registration_type == "Exhibitor":
			exhibitor = frappe.get_doc({
				"doctype": "Exhibitor",
				"participant": self.name,
				"event":self.event,
				"stall": self.stall,
				"other_attendees": self.other_attendees
			})
			exhibitor.insert()
		if not self.event:
			frappe.throw("Event is required to determine time zone")
		time_zone = frappe.db.get_value(
			"Conference",
			self.event,
			"time_zone"
		)
		if not time_zone:
			frappe.throw(f"Please set Time Zone for Conference: {self.event}")
		# Find or create User
		user = frappe.db.get_value("User", {"email": self.e_mail}, "name")
		if user:
			user_doc = frappe.get_doc("User", user)
			if user_doc.user_type != "System User":
				# Update the user to be a System User and fill missing details
				user_doc.update({
					"user_type": "System User",
					"first_name": self.first_name or user_doc.first_name,
					"last_name": self.last_name or user_doc.last_name,
					"mobile_no": self.mobile_number or user_doc.mobile_no,
					"time_zone": time_zone or user_doc.time_zone,
					"send_welcome_email": 1,
					"module_profile": "E-desk profile"
				})
				if not any(role.role == "Participant" for role in user_doc.roles):
					user_doc.append("roles", {"role": "Participant"})
				user_doc.save(ignore_permissions=True)
				frappe.db.commit()

			print("\n\n\n\nuser doc", user_doc)
		else:
			print("\n\n\n NO USERRRRRRRRRRRRRR")
			user_doc = frappe.new_doc("User")
			user_doc.update({
				"email": self.e_mail,
				"first_name": self.first_name,
				"last_name": self.last_name,
				"mobile_no": self.mobile_number,
				"time_zone": time_zone,
				"user_type": "System User",
				# "new_password":self.mobile_number,
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
		
		self.create_address_and_contact()
		print("address and contact created and linked.............")


	def validate(self):
		self.sync_contact_details()
		self.set_full_name()

	def before_insert(self):
		if not self.event_role:
			self.event_role = "Participant"


	def is_customer_creation_enabled(self):
	# 	return frappe.db.get_value(
	# 		"Conference Settings",
	# 		"create_customer_on_participant_creation"
	# 	)
		return frappe.db.get_single_value(
					"Conference Settings",
					"create_customer_on_participant_creation"
				)


	def set_full_name(self):
		self.full_name = f"{self.first_name} {self.last_name}"

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


	def create_customer(self):
		print("creating customer..............")
		if not self.set_full_name:
			self.set_full_name()

		customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": self.full_name,
        "customer_type": "Individual",
		}).insert(ignore_permissions=True)
		self.db_set("customer", customer.name)

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
        user.user_type = "System User"
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
	settings = frappe.get_single("Conference Settings")
	return {
		"has_meal": settings.has_meal,
		"meal_access": settings.meal_access
	}
@frappe.whitelist(allow_guest=True)
def get_meal_settings_for_webform():
	settings = frappe.get_single("Conference Settings")
	result = {
		"has_meal": settings.has_meal,
		"meal_access": settings.meal_access,
		"meal_item": settings.meal_item	}

	if not settings.has_meal or not settings.meal_item:
		return result
	customer = frappe.db.get_value(
		"Portal User",
		{"user": frappe.session.user},
		"parent"
	)
	if not customer:
		return result	
	return result