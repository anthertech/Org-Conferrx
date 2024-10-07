// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Category-wise Registration Report"] = {
	"filters": [
		{
			"fieldname": "category",
			"label": __("Category Name"),
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