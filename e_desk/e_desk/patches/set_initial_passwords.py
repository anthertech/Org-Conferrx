import frappe
from e_desk.e_desk.utils.password_utils import build_initial_password

def execute(dry_run=True):
    """Patch script to set initial passwords for Participant-linked users.
    Runs in dry-run mode by default and prints actions. Set dry_run=False to apply.
    """
    participants = frappe.get_all("Participant", filters={}, fields=["name", "e_mail", "mobile_number", "user"])
    actions = []
    for p in participants:
        if not p.get('e_mail'):
            continue
        user_name = p.get('user')
        if not user_name:
            # find user by email
            user_name = frappe.db.get_value("User", {"email": p.get('e_mail')}, "name")
        if not user_name:
            continue
        password = build_initial_password(p.get('e_mail'), p.get('mobile_number'))
        actions.append((user_name, password))

    for user_name, password in actions:
        if dry_run:
            print(f"DRY RUN: Would set password for {user_name} -> {password}")
        else:
            try:
                user = frappe.get_doc("User", user_name)
                user.new_password = password
                user.save(ignore_permissions=True)
                print(f"Set password for {user_name}")
            except Exception as e:
                print(f"Failed to set for {user_name}: {e}")
