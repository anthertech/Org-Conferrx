# file: e_desk/api/cart.py
import frappe
from frappe.utils import flt

@frappe.whitelist()
def add_to_cart(item_code, user=None, event=None, warehouse=None, serial_no=None):
    """
    Add an item to the cart (Sales Invoice Draft) for this participant.
    Backward compatible with old calls.
    """

    # ------------------------------------------------
    # 1. Resolve user safely
    # ------------------------------------------------
    if not user:
        user = frappe.session.user

    # ------------------------------------------------
    # 2. Get participant + customer
    # ------------------------------------------------
    participant = frappe.db.get_value(
        "Participant",
        {"user": user},
        ["name", "customer"],
        as_dict=True
    )

    print("\n\n\n\nparticipant\n",participant)

    if not participant:
        frappe.throw("No participant record found for this user.")

    if not participant.customer:
        frappe.throw("No customer linked to this participant.")

    customer = participant.customer

    # ------------------------------------------------
    # 3. Item validation
    # ------------------------------------------------
    item = frappe.get_doc("Item", item_code)

    # Serial validation (only if item is serialized)
    if item.has_serial_no:
        if not serial_no:
            frappe.throw("Slot selection is required for this item.")

        if not warehouse:
            frappe.throw("Warehouse is required for slot-based items.")

        valid_serial = frappe.db.exists(
            "Serial No",
            {
                "name": serial_no,
                "item_code": item_code,
                "warehouse": warehouse,
                "status": "Available"
            }
        )

        if not valid_serial:
            frappe.throw("Selected slot is no longer available.")

    # ------------------------------------------------
    # 4. Find existing draft invoice (EVENT AWARE)
    invoice_filters = {
        "customer": customer,
        "docstatus": 0
    }

    # 🔑 Isolate cart per warehouse (EVENT)
    if warehouse:
        invoice_filters["set_warehouse"] = warehouse

    print("\n\nInvoice Filters:", invoice_filters)

    si_name = frappe.db.get_value(
        "Sales Invoice",
        invoice_filters,
        "name"
    )
    print("\n\n\si_name",si_name)
    print("\n\n\n\n")
    # ------------------------------------------------
    # 5. Create or load draft invoice
    # ------------------------------------------------
    if si_name:
        si = frappe.get_doc("Sales Invoice", si_name)
    else:
        si_data = {
            "doctype": "Sales Invoice",
            "customer": customer,
            "status": "Draft",
            "items": []
        }

        if event:
            si_data["event"] = event

        if warehouse:
            si_data["source_warehouse"] = warehouse

        si = frappe.get_doc(si_data)

    # ------------------------------------------------
    # 6. Append item (warehouse + serial safe)
    # ------------------------------------------------
    si.append("items", {
        "item_code": item.item_code,
        "item_name": item.item_name,
        "qty": 1,
        "warehouse": warehouse,
        "serial_no": serial_no
    })

    # ------------------------------------------------
    # 7. Save
    # ------------------------------------------------
    si.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Item added to cart",
        "invoice": si.name
    }



@frappe.whitelist(allow_guest=True)
def get_cart_for_user():
    user = frappe.session.user

    participant = frappe.db.get_value(
        "Participant", {"user": user},
        ["customer"], as_dict=True
    )

    if not participant or not participant.customer:
        return {"items": []}

    invoice_name = frappe.db.get_value(
        "Sales Invoice",
        {"customer": participant.customer, "docstatus": 0},
        "name"
    )

    if not invoice_name:
        return {"items": []}

    si = frappe.get_doc("Sales Invoice", invoice_name)

    items = []
    for row in si.items:
        items.append({
            "rowname": row.name,
            "item_name": row.item_name,
            "qty": row.qty,
            "rate": row.rate,
            "amount": row.amount,
            "is_free": row.rate == 0
        })

    return {
        "invoice": si.name,
        "items": items,
        "net_total": si.net_total,
        "total_taxes": si.total_taxes_and_charges,
        "rounded_total": si.rounded_total,
        "grand_total": si.grand_total
    }
@frappe.whitelist()
def update_cart_qty(rowname, delta):
    row = frappe.get_doc("Sales Invoice Item", rowname)
    si = frappe.get_doc("Sales Invoice", row.parent)

    new_qty = row.qty + int(delta)
    if new_qty < 1:
        return

    for item in si.items:
        if item.name == rowname:
            item.qty = new_qty
            break

    si.save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def remove_cart_item(rowname):
    row = frappe.get_doc("Sales Invoice Item", rowname)
    parent = row.parent
    row.delete()
    frappe.get_doc("Sales Invoice", parent).save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def checkout_cart():
    user = frappe.session.user

    participant = frappe.db.get_value(
        "Participant",
        {"user": user},
        ["customer"],
        as_dict=True
    )

    if not participant or not participant.customer:
        frappe.throw("Customer not linked")

    invoice_name = frappe.db.get_value(
        "Sales Invoice",
        {"customer": participant.customer, "docstatus": 0},
        "name"
    )

    if not invoice_name:
        frappe.throw("No draft invoice found")

    si = frappe.get_doc("Sales Invoice", invoice_name)

    if not si.items:
        frappe.throw("Cart is empty")

    si.submit()
    frappe.db.commit()

    return {
        "invoice": si.name
    }
