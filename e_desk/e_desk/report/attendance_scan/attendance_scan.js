// Copyright (c) 2024, anthertech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Scan"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
	
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "registration_no",
			"label": __("Registration No"),
			"fieldtype": "Data",
		},
	],
	"initial_depth":0,
 "formatter":function(value, row, column, data, default_formatter) {
  return default_formatter(value, row, column, data)
 }
};
