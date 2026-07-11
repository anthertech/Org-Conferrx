import frappe


def execute():
    users = frappe.db.sql("""
        SELECT DISTINCT h.parent
        FROM `tabHas Role` h
        INNER JOIN `tabUser` u ON u.name = h.parent
        WHERE h.role = 'Sales User'
        AND u.enabled = 1
        AND h.parent NOT IN (
            SELECT parent FROM `tabHas Role` WHERE role = 'Projects Manager'
        )
    """, as_dict=True)

    updated = 0
    for row in users:
        if not frappe.db.exists("User", row.parent):
            continue
        user = frappe.get_doc("User", row.parent)
        roles_to_keep = [r for r in user.roles if r.role != "Sales User"]
        if len(roles_to_keep) != len(user.roles):
            user.roles = roles_to_keep
            user.save(ignore_permissions=True)
            updated += 1

    frappe.db.commit()
    print(f"Removed Sales User role from {updated} users")
