frappe.query_reports["Attendee Report"] = {
    "filters": [
        {
            "fieldname": "programme",
            "label": __("Programme"),
            "fieldtype": "Select",
            "depends_on": "eval:doc.confer"
        },
        {
            "fieldname": "confer",
            "label": __("Confer"),
            "fieldtype": "Link",
            "options": "Confer",
            "reqd": 1,
            "on_change": function () {
                // Trigger when confer is selected
                var confer = frappe.query_report.get_filter_value('confer');
                if (confer) {
                    console.log(confer, "Selected confer...");

                    // Clear programme selection
                    frappe.query_report.set_filter_value('programme', "");

                    // Fetch programme options based on selected confer
                    frappe.call({
                        method: "e_desk.e_desk.report.attendee_report.attendee_report.confer_agenda_list",
                        args: {
                            confer: confer
                        },
                        callback: function (r) {
                            var options = [];
                            if (r.message) {
                                console.log(r.message, "Programmes fetched...");

                                // Map the response directly
                                options = r.message; // Simplified array of options

                                // Access the filters using frappe.query_report.filters
                                let programme_filter = frappe.query_report.filters.find(f => f.fieldname === 'programme');
                                console.log(programme_filter, "programme_filter");

                                // Check if the programme filter exists
                                if (programme_filter) {
                                    programme_filter.df.options = options;
                                    programme_filter.refresh();
                                    console.log("Programme options updated:", options);
                                } else {
                                    console.error("Programme filter is not defined. Check the fieldname or initialization.");
                                }
                            } else {
                                console.error("No message received from the server.");
                            }
                        }
                    });
                }
            }
        }
    ]
};
