// Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Conference Programme Agenda", {
	refresh(frm) {
        set_speaker_query(frm);
	},

    conference(frm) {
		frm.set_value("speakers", []);
		set_speaker_query(frm);
	},
});

function set_speaker_query(frm) {
	frm.set_query("speakers", () => {
		return {
			filters: {
				conference: frm.doc.conference,
			},
            ignore_user_permissions: 1
		};
	});
}