import frappe

@frappe.whitelist(allow_guest=True)
def get_stall_items():
    return frappe.get_all(
        "Item",
        filters={"item_group": "Stall"},
        fields=["name", "custom_max_staff_allowed"],
        ignore_permissions=True  # IMPORTANT for Guest
    )
