// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt
frappe.ui.form.on('Voting Topic', {
    scan_qr: function(frm) {
        if (frm.doc.scan_qr) {
            var name = JSON.parse(frm.doc.scan_qr).name;
            var duplicateFound = false;
            frm.doc.voting.forEach(function(row) {
                if (row.participant === name) {
                    duplicateFound = true;
                    return false; 
                }
            });

            if (!duplicateFound) {
                var item = frm.add_child("voting");
                frappe.model.set_value(item.doctype, item.name, "participant", name);
                frm.refresh_field('voting');

                frm.set_value("scan_qr", '');
                var childTableLength = frm.doc.voting.length;
                frm.set_value("vote_count", childTableLength);

                frm.save();
            } else {
                frm.set_value("scan_qr", '');
                frappe.msgprint(__("You Already Voted"));
            }
        }
    }
});



