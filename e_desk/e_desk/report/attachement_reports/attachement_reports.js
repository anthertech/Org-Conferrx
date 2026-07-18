// Copyright (c) 2024, sathya and contributors
// For license information, please see license.txt


frappe.query_reports["Attachement Reports"] = {
    filters: [
        {
            fieldname: "confer_id",
            label: __("Confer ID"),
            fieldtype: "Link",
            options: "Conference",
            reqd: 1,
            default: ""
        }
    ],

	onload: function(report) {
     
        frappe.call({
            method: "e_desk.e_desk.report.attachement_reports.attachement_reports.get_current_confer",  // Adjust to your server method path
            callback: function(response) {
                if (response.message) {
					console.log(response.message,"this is message")
                    // Set the default value of the confer_id filter
                    report.set_filter_value("confer_id", response.message);
                }
            }
        });

        // Add a reload button to the report
        report.page.add_inner_button(__("Reload"), function() {
            report.refresh();
        });
    }


};