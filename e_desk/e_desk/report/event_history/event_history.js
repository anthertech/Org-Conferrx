// Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.query_reports["Event History"] = {
    filters: [
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "email",
            label: __("User"),
            fieldtype: "Link",
            options: "User",
            default: frappe.session.user
        },
        {
            fieldname: "event",
            label: __("Event"),
            fieldtype: "Link",
            options: "Conference",
        }
    ],
};

