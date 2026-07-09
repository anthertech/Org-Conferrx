import frappe


def execute():
	participants = frappe.get_all(
		"Participant",
		fields=["name", "first_name", "last_name"]
	)

	updated = 0
	for p in participants:
		parts = [p.first_name, p.last_name] if p.last_name else [p.first_name]
		correct_name = " ".join(parts)
		if not correct_name:
			correct_name = p.first_name or ""

		current = frappe.db.get_value("Participant", p.name, "full_name")
		if current != correct_name:
			frappe.db.set_value(
				"Participant", p.name, "full_name",
				correct_name, update_modified=False
			)
			updated += 1

	frappe.db.commit()
	print(f"Fixed full_name for {updated} participants")