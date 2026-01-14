// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Programme Attendance', {

    scan_qr: function(frm) {
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
                        frm.reload_doc();
                        frm.set_value("scan_qr", "");
                    }
                }
            });
     },

    event: function (frm) {
        frm.set_value("choose_programme", "");
        frm.set_df_property("choose_programme", "options", "");

        if (!frm.doc.event) {
            return;
        }

        frappe.call({
            method: "e_desk.e_desk.doctype.programme_attendance.programme_attendance.get_programmes",
            args: {
                confer: frm.doc.event
            },
            callback: function (r) {
                if (r.message && r.message.length) {
                    let options = [""];

                    r.message.forEach(programme => {
                        options.push(programme);
                    });

                    frm.set_df_property(
                        "choose_programme",
                        "options",
                        options.join("\n")
                    );
                } else {
                    frm.set_df_property("choose_programme", "options", "");
                }
            }
        });
    },
	
	choose_programme: function(frm) {
        if (frm.doc.choose_programme) {
            console.log(frm.doc.choose_programme, "Programme selected, saving data...");
            frm.save_or_update();  
        }
    },
	});