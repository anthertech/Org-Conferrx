# Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
# from frappe.core.doctype.user.user import get_roles
from frappe.utils import get_datetime, add_to_date , now ,getdate
from datetime import datetime, time, timedelta
from e_desk.e_desk.doctype.registration_desk.registration_desk import RegistrationDesk 


class Participant(Document):

	def after_insert(self):
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
					"send_welcome_email": 0,
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
				"send_welcome_email": 0,
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

		if not self.customer:
			print("no customer in this participant")
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
		if not self.customer:
			return
		print("customer exist", self.customer)
		address_name = frappe.db.get_value(
			"Dynamic Link",
			{
				"link_doctype": "Customer",
				"link_name": self.customer,
				"parenttype": "Address",
			},
			"parent"
		)

		if not address_name:
			print("new address creating........")
			address = frappe.get_doc({
				"doctype": "Address",
				"address_type": "Billing",
				"address_line1": self.address_line_1,
				"city": self.city,
				"state": self.state,
				"country": self.country,
				"pincode": self.postal_code,
				"links": [{"link_doctype": "Customer", "link_name": self.customer}],
			})
			address.insert(ignore_permissions=True)
			address_name = address.name

		# Set primary address if missing
		if not frappe.db.get_value("Customer", self.customer, "customer_primary_address"):
			frappe.db.set_value(
				"Customer",
				self.customer,
				"customer_primary_address",
				address_name
			)
			print("addrs linked to customer primary addrs")
		# Link Address → Participant
		if not frappe.db.exists(
			"Dynamic Link",
			{
				"parenttype": "Address",
				"parent": address_name,
				"link_doctype": "Participant",
				"link_name": self.name,
			},
		):
			print("addrs linked with participant")
			frappe.get_doc("Address", address_name).append(
				"links",
				{"link_doctype": "Participant", "link_name": self.name}
			).save(ignore_permissions=True)

		self.db_set("participant_address", address_name)

		contact_name = frappe.db.get_value(
			"Dynamic Link",
			{
				"link_doctype": "Customer",
				"link_name": self.customer,
				"parenttype": "Contact",
			},
			"parent"
		)
		if not contact_name:
			print("new contact in cust ............")
			contact = frappe.get_doc({
				"doctype": "Contact",
				"first_name": self.first_name or self.customer,
				"links": [{"link_doctype": "Customer", "link_name": self.customer}],
			})

			if self.e_mail:
				contact.append("email_ids", {
					"email_id": self.e_mail,
					"is_primary": 1,
				})

			if self.mobile_number:
				contact.append("phone_nos", {
					"phone": self.mobile_number,
					"is_primary_phone": 1,
				})

			contact.insert(ignore_permissions=True)
			contact_name = contact.name
			print("contact created")

		# Set primary contact if missing
		if not frappe.db.get_value("Customer", self.customer, "customer_primary_contact"):
			frappe.db.set_value(
				"Customer",
				self.customer,
				"customer_primary_contact",
				contact_name
			)

		# Link Contact → Participant
		if not frappe.db.exists(
			"Dynamic Link",
			{
				"parenttype": "Contact",
				"parent": contact_name,
				"link_doctype": "Participant",
				"link_name": self.name,
			},
		):
			print("contact added in participant................")
			frappe.get_doc("Contact", contact_name).append(
				"links",
				{"link_doctype": "Participant", "link_name": self.name}
			).save(ignore_permissions=True)
		self.db_set("participant_contact", contact_name)
		print("contact address finished...................")


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
def update_event_volunteer(participant):
    if not frappe.has_permission("Participant", "write"):
        frappe.throw("Not permitted")

    participant_doc = frappe.get_doc("Participant", participant)
    make_volunteer = not participant_doc.volunteer
    participant_doc.volunteer = 1 if make_volunteer else 0
    participant_doc.save(ignore_permissions=True)

    if not participant_doc.user:
        return
    user = frappe.get_doc("User", participant_doc.user)
    if make_volunteer:
        if "Volunteer" not in [r.role for r in user.roles]:
            user.append("roles", {"role": "Volunteer"})
            user.user_type = "System User"
        perms = frappe.get_all(
            "User Permission",
            filters={
                "user": user.name,
                "allow": ["!=", "Conference"]
            },
            pluck="name"
        )
        for p in perms:
            frappe.delete_doc("User Permission", p, ignore_permissions=True)
    else:
        user.roles = [r for r in user.roles if r.role != "Volunteer"]
        if not frappe.db.exists(
            "User Permission",
            {
                "user": user.name,
                "allow": "User",
                "for_value": user.name
            }
        ):
            frappe.get_doc({
                "doctype": "User Permission",
                "user": user.name,
                "allow": "User",
                "for_value": user.name
            }).insert(ignore_permissions=True)

    user.save(ignore_permissions=True)


@frappe.whitelist()
def update_event_speaker(participant):
    if not frappe.has_permission("Participant", "write"):
        frappe.throw("Not permitted")
    participant_doc = frappe.get_doc("Participant", participant)
    # Toggle speaker checkbox only
    participant_doc.speaker = 0 if participant_doc.speaker else 1
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
		"meal_item": settings.meal_item,
		"has_purchased_meal": 0
	}

	# Stop early if no meal
	if not settings.has_meal or not settings.meal_item:
		return result

	# Get Customer from User (portal user → contact → customer)
	customer = frappe.db.get_value(
		"Portal User",
		{"user": frappe.session.user},
		"parent"
	)

	if not customer:
		return result

	# Find delivered / active sales orders
	sales_orders = frappe.get_all(
		"Sales Order",
		filters={
			"customer": customer,
			"docstatus": 1
		},
		pluck="name"
	)

	if not sales_orders:
		return result

	# Check if meal item exists in SO Items
	exists = frappe.db.exists(
		"Sales Order Item",
		{
			"parent": ["in", sales_orders],
			"item_code": settings.meal_item,
			"qty": [">", 0]
		}
	)

	if exists:
		result["has_purchased_meal"] = 1
	print(result)
	return result
