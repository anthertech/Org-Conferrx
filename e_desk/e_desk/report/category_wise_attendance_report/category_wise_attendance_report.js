// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Category-wise Attendance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd":1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd":1

		},
		{
			"fieldname": "category",
			"label": ("Category Name"),
			"fieldtype": "Link",
			'options':"Category Name"
		},
		{
			"fieldname": "reg_no",
			"label": ("Reg No"),
			"fieldtype": "Data",
		},
	],
	"initial_depth":0,
	"formatter":function(value, row, column, data, default_formatter) {
	return default_formatter(value, row, column, data)
	}
};