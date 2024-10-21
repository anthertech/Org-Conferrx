frappe.query_reports["Attendee Report"] = {
    "filters": [
    
        {
            "fieldname": "confer",
            "label": __("Confer"),
            "fieldtype": "Link",
            "options": "Confer",
            "reqd": 1,
       
        },
   
        {
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),  // Optional: Sets the default to today's date
            "depends_on": "eval:doc.confer",  // You can apply conditions similar to the programme field
            "on_change": function () {
                // Trigger when confer is selected
                var confer = frappe.query_report.get_filter_value('confer');
                var date_value=frappe.query_report.get_filter_value('date');
                if (confer) {
                    console.log(confer, "Selected confer...");

                    // Clear programme selection
                    frappe.query_report.set_filter_value('programme', "");

                    // Fetch programme options based on selected confer
                    frappe.call({
                        method: "e_desk.e_desk.report.attendee_report.attendee_report.confer_agenda_list",
                        args: {
                            confer: confer,
                            date_value:date_value
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
        },
        {
            "fieldname": "programme",
            "label": __("Programme"),
            "fieldtype": "Select",
            "depends_on": "eval:doc.confer"
        },
    ]
};
