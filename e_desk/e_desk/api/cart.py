# file: e_desk/api/cart.py
import frappe
from frappe.utils import flt

# file: e_desk/api/cart.py
import frappe

@frappe.whitelist()
def add_to_cart(item_code, user=None, event=None, warehouse=None, serial_no=None):
    """
    Add an item to the cart (Sales Invoice Draft) for this participant.
    Merges serialized and non-serialized items in a single row.
    """

    # 1. Resolve user safely
    if not user:
        user = frappe.session.user

    # 2. Get participant + customer
    participant = frappe.db.get_value(
        "Participant",
        {"user": user},
        ["name", "customer"],
        as_dict=True
    )
    if not participant:
        frappe.throw("No participant record found for this user.")
    if not participant.customer:
        frappe.throw("No customer linked to this participant.")
    customer = participant.customer

    # 3. Get project from Conference if event provided
    project = None
    if event:
        project = frappe.db.get_value("Conference", {"name": event}, "project")

    # 4. Item validation
    item = frappe.get_doc("Item", item_code)

    # 5. Find existing draft invoice
    invoice_filters = {
        "customer": customer,
        "docstatus": 0
    }
    if warehouse:
        invoice_filters["set_warehouse"] = warehouse

    si_name = frappe.db.get_value("Sales Invoice", invoice_filters, "name")

    if si_name:
        si = frappe.get_doc("Sales Invoice", si_name)
    else:
        si_data = {
            "doctype": "Sales Invoice",
            "customer": customer,
            "update_stock": 1,
            "set_warehouse": warehouse,
            "project": project,
            "status": "Draft",
            "items": []
        }
        si = frappe.get_doc(si_data)

    # 6. Serial number validation (after invoice exists)
    if item.has_serial_no:
        if not serial_no:
            frappe.throw("Slot selection is required for this item.")
        if not warehouse:
            frappe.throw("Warehouse is required for slot-based items.")

        # Check serial exists in stock
        valid_serial = frappe.db.exists(
            "Serial No",
            {"name": serial_no, "item_code": item_code, "warehouse": warehouse, "status": "Active"}
        )
        if not valid_serial:
            frappe.throw("Selected slot is no longer available.")

    # 7. Merge items
    existing_row = None
    for row in si.items:
        if row.item_code == item.item_code and row.warehouse == warehouse:
            existing_row = row
            break

    # 8. Append serial or increment quantity
    if existing_row:
        # Serialized item: append serial_no
        if item.has_serial_no:
            if existing_row.serial_no:
                # avoid duplicates
                serials = existing_row.serial_no.split(",")
                if serial_no in serials:
                    frappe.throw("This slot is already in your cart.")
                serials.append(serial_no)
                existing_row.serial_no = ",".join(serials)
            else:
                existing_row.serial_no = serial_no
            existing_row.qty += 1
        else:
            # Non-serialized: just increment qty
            existing_row.qty += 1
    else:
        # New row
        si.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": 1,
            "use_serial_batch_fields": 1 if item.has_serial_no else 0,
            "warehouse": warehouse if item.has_serial_no or item.is_stock_item else None,
            "serial_no": serial_no if item.has_serial_no else None,
            "project": project
        })

    # 9. Save
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
            "is_free": row.rate == 0,
            "is_serialized":row.use_serial_batch_fields == 1
        })

    return {
        "invoice": si.name,
        "items": items,
        "net_total": si.net_total,
        "total_taxes": si.total_taxes_and_charges,
        "rounded_total": si.rounded_total,
        "grand_total": si.grand_total,
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


# @frappe.whitelist()
# def remove_cart_item(rowname):
#     row = frappe.get_doc("Sales Invoice Item", rowname)
#     parent = row.parent
#     row.delete()
#     frappe.get_doc("Sales Invoice", parent).save(ignore_permissions=True)
#     frappe.db.commit()

@frappe.whitelist()
def remove_cart_item(rowname):
    row = frappe.get_doc("Sales Invoice Item", rowname)
    si = frappe.get_doc("Sales Invoice", row.parent)

    # ------------------------------------
    # 1. Remove the selected row
    # ------------------------------------
    row.delete()

    # ------------------------------------
    # 2. Remove orphan FREE items
    # ------------------------------------
    for item in list(si.items):
        if item.rate == 0:
            # optional: tighten rule if needed
            item.delete()

    # ------------------------------------
    # 3. If no items left → delete invoice
    # ------------------------------------
    if not si.items:
        si.delete(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "invoice_deleted"}

    # ------------------------------------
    # 4. Save invoice
    # ------------------------------------
    si.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "item_removed"}


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
