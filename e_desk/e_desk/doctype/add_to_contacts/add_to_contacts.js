frappe.ui.form.on("Add to Contacts", {
    scan_qr(frm) {
        if (!frm.doc.scan_qr) return;

        let scanned_id = frm.doc.scan_qr;
        let email = frappe.session.user;

        // Step 1: Get logged-in participant
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "User",
                fieldname: "participant_id",
                filters: { email: email }
            },
            callback(res) {

                if (!res.message || !res.message.participant_id) {
                    frappe.msgprint("Your User Account is not linked to any Participant.");
                    frm.set_value("scan_qr", "");
                    return;
                }

                let current_participant = res.message.participant_id;

                // Step 2: Call your Python API first
                frappe.call({
                    method: "e_desk.e_desk.doctype.participant.participant.connection_doc",
                    args: {
                        doc_name: scanned_id,
                        email: email
                    },
                    callback(r) {

                        if (r.exc) {
                            frappe.msgprint("This participant is already connected.");

                            // DO NOT SET any fields
                            frm.set_value("scan_qr", "");

                            frm.dirty(false);
                            frm.doc.__unsaved = false;
                            return;
                        }

                        if (r.message) {

                            frm.set_value("added_by", current_participant);
                            frm.set_value("scanned_participant", scanned_id);

                            setTimeout(() => {
                                frm.save().then(() => {

                                    frm.reload_doc();

                                    frm.set_value("scan_qr", "");
                                    frm.dirty(false);
                                    frm.doc.__unsaved = false;
                                });
                            }, 300);

                        } else {
                            frappe.msgprint("Something went wrong.");
                            frm.set_value("scan_qr", "");
                        }
                    }
                });

            }
        });
    }
});
