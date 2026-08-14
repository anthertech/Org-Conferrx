frappe.query_reports["Attendee Report"] = {
    filters: [
        {
            fieldname: "confer",
            label: __("Conference"),
            fieldtype: "Link",
            options: "Conference",
            reqd: 1,
            on_change: function () {
                load_programmes();
            }
        },
        {
            fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
            on_change: function () {
                load_programmes();
            }
        },
        {
            fieldname: "programme",
            label: __("Programme"),
            fieldtype: "Select",
            reqd: 1
        }
    ]
};


function load_programmes() {
    let confer = frappe.query_report.get_filter_value("confer");
    let date_value = frappe.query_report.get_filter_value("date");

    frappe.query_report.set_filter_value("programme", "");

    let programme_filter = frappe.query_report.get_filter("programme");
    programme_filter.df.options = "\n";
    programme_filter.refresh();

    if (!confer || !date_value) {
        return;
    }

    frappe.call({
        method: "e_desk.e_desk.report.attendee_report.attendee_report.confer_agenda_list",
        args: {
            confer: confer,
            date_value: date_value
        },
        callback: function (r) {
            let options = [""];

            if (r.message && r.message.length) {
                r.message.forEach(function (programme) {
                    options.push(programme);
                });
            }

            programme_filter.df.options = options.join("\n");
            programme_filter.refresh();
        }
    });
}