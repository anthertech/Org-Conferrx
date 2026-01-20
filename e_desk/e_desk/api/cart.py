# file: e_desk/api/cart.py
import frappe
from frappe.utils import flt

@frappe.whitelist()
def add_to_cart(item_code, user):
    """
    Add an item to the cart (Sales Invoice Draft) for this participant.
    """
    # Get customer linked to participant
    participant = frappe.db.get_value(
        "Participant",
        {"user": user},
        ["name", "customer"],  # we need customer too
        as_dict=True
    )
    if not participant:
        frappe.throw("No participant record found for this user.")
    if not participant.customer:
        frappe.throw("No customer linked to this participant.")

    customer = participant.customer

    # Check if a draft Sales Invoice exists for this customer
    si_name = frappe.db.get_value(
        "Sales Invoice",
        {"customer": customer, "docstatus": 0},  # Draft
        "name"
    )

    # Get item details
    item_doc = frappe.get_doc("Item", item_code)

    if si_name:
        # Draft invoice exists → append item
        si = frappe.get_doc("Sales Invoice", si_name)
    else:
        # Create new draft Sales Invoice
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "status": "Draft",
            "items": []
        })

    # Append the item
    si.append("items", {
        "item_code": item_doc.item_code,
        "item_name": item_doc.item_name,
        # "rate": item_doc.standard_rate,
        "qty": 1
    })

    si.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Item added to cart", "invoice": si.name}




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
