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

			# here check their previous participant record and customer field value there, and assign that customer to here and 
		else:
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

		# User Permission for Conference and User
		if self.event and not frappe.db.exists("User Permission", {
			"user": self.e_mail,
			"allow": "Conference",
			"for_value": self.event
		}):
			self.create_user_permissions()
		if not self.customer:
			existing_customer = self.get_existing_customer_from_previous_participant()
			if existing_customer:
				self.db_set("customer", existing_customer)
			else:
				self.create_customer()
		self.create_address_and_contact()

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

		# 1. Create Address
		address = frappe.get_doc({
			"doctype": "Address",
			"address_title": self.address_title,
			"address_type": "Billing", 
			"address_line1": self.address_line_1,
			"address_line2":self.address_line_2,
			"city": self.city,
			"state": self.state,
			"country": self.country,
			"links": [
				{
					"link_doctype": "Customer",
					"link_name": self.customer,
				},
				{
					"link_doctype": "Participant",
					"link_name": self.name,
				},
			],
		})
		address.insert(ignore_permissions=True)

		# 2. Create Contact
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": self.customer,
			"links": [
				{
					"link_doctype": "Customer",
					"link_name": self.customer,
				},
				{
					"link_doctype": "Participant",
					"link_name": self.name,
				},
			],
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
		self.db_set("participant_address", address.name)
		self.db_set("participant_contact", contact.name)
		frappe.db.set_value("Customer", self.customer, "customer_primary_address", address.name)
		frappe.db.set_value("Customer", self.customer, "customer_primary_contact", contact.name)


	def create_customer(self):
		if not self.set_full_name:
			self.set_full_name()

		customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": self.full_name,
        "customer_type": "Individual",
		}).insert(ignore_permissions=True)
		self.db_set("customer", customer.name)

	def get_existing_customer_from_previous_participant(self):
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



	def sync_contact_details(self):
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
    """
    scanned_user = QR value (User ID that was scanned)
    email        = current User email (scanner)
    """

    # 1️⃣ Check if connection already exists
    exists = frappe.db.exists(
        "Connections",
        {
            "participant_id": email,     # ME
            "email": scanned_user         # PERSON I SCANNED
        }
    )

    if exists:
        return {"status": "exists"}

    # 2️⃣ Get scanned user's details
    scanned = frappe.get_doc("User", scanned_user)

    # 3️⃣ Create new connection
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
