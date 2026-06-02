// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Programme Attendance", {
    refresh: function (frm) {
        if (frm.doc.event) {
            frm.events.load_programmes(frm);
        }
    },

    event: function (frm) {
        frm.set_value("choose_programme", "");
        frm.events.load_programmes(frm);
    },

    scan_qr: function (frm) {
        if (frm.doc.scan_qr) {
            frm.events.submit(frm);
        }
    },

    submit: function (frm) {
        if (!frm.doc.scan_qr) return;

        frappe.call({
            method: "e_desk.e_desk.doctype.programme_attendance.programme_attendance.process_scan",
            args: {
                scan_qr: frm.doc.scan_qr,
                event: frm.doc.event,
                programme: frm.doc.choose_programme,
                docname: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("scan_qr", "");

                    frappe.show_alert({
                        message: __("Scan successful"),
                        indicator: "green"
                    }, 2);
                }
            }
        });
    },

    choose_programme: function (frm) {
        if (frm.doc.choose_programme) {
            console.log(frm.doc.choose_programme, "Programme selected");
        }
    },

    load_programmes: function (frm) {
        frm.set_df_property("choose_programme", "options", "\n");
        frm.refresh_field("choose_programme");

        if (!frm.doc.event) return;

        frappe.call({
            method: "e_desk.e_desk.doctype.programme_attendance.programme_attendance.get_programmes",
            args: {
                confer: frm.doc.event
            },
            callback: function (r) {
                console.log("get_programmes response:", r.message);

                if (r.message && r.message.length) {
                    let options = [""];

                    r.message.forEach(function (programme) {
                        options.push(programme);
                    });

                    frm.set_df_property(
                        "choose_programme",
                        "options",
                        options.join("\n")
                    );
                } else {
                    frm.set_df_property("choose_programme", "options", "\n");

                    frappe.msgprint(
                        __("No scannable programme found for this event.")
                    );
                }

                frm.refresh_field("choose_programme");
            }
        });
    }
});