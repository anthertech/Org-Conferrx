// Copyright (c) 2024, anthertech and contributors
// For license information, please see license.txt

frappe.query_reports["Test attendance Scan"] = {
	filters: [
		{
			"fieldname": "event",
			"label": __("Event"),
			"fieldtype": "Link",
			"options":"Confer",
			"reqd": 1,
		},
	],
};
