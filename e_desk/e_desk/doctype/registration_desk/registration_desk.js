// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

let current_item_group = "";

frappe.ui.form.on('Registration Desk', {

	onload(frm) {
		update_item_group(frm);
	},

	confer(frm) {
		update_item_group(frm);
	},

	scan_qr(frm) {
		if (!frm.doc.scan_qr) return;

        if (!frm.doc.confer) {
			frm.set_value("scan_qr", "");
            frappe.throw("Please Select an Event First");
            return; // ensure nothing else runs
        }
        frappe.call({
            method: "e_desk.e_desk.doctype.registration_desk.registration_desk.registration_details",
            args: {
                user: frm.doc.scan_qr,
                confer: frm.doc.confer
            },
            callback(r) {
                if (!r.message) return;

                // Clear scan
                frm.set_value("scan_qr", "");

                // Set fields
                frm.set_value("participant_id", r.message.participant_id);
                frm.set_value("participant_name", r.message.full_name);
                frm.set_value("part_profile", r.message.profile_photo);
                frm.set_value("qr_profile", r.message.qr);
                frm.set_value("customer", r.message.customer || "");

                // Render profile photo
                if (r.message.profile_photo) {
                    frm.get_field("profile_preview").$wrapper.html(`
                        <img src="${r.message.profile_photo}" height="100">
                    `);
                }

                // Render QR
                if (r.message.qr) {
                    frm.get_field("qr_preview").$wrapper.html(`
                        <img src="${r.message.qr}" height="100">
                    `);
                }
            }
        });
    },

	refresh(frm) {

		if (frm.doc.part_profile) {
			let imgHTML = `
				<div>
					<img src="${frm.doc.part_profile}" alt="Profile Image" style="width:116px !important; 
									border-radius:5px;">
				</div>`;
			frm.get_field("profile_preview").$wrapper.html(imgHTML);
		}

		if (frm.doc.qr_profile) {
			let qrHTML = `
				<div>
					<img src="${frm.doc.qr_profile}" alt="QR Code"
						style="width:116px !important; border-radius:5px;">
				</div>`;
			frm.get_field("qr_preview").$wrapper.html(qrHTML);
		}

		frm.set_query('item', 'items', () => {
			let filters = { 'disabled': 0 };
			if (current_item_group) {
				filters['item_group'] = current_item_group;
			}
			return { filters: filters };
		});

		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Sales Invoice'), () => {
				frappe.model.open_mapped_doc({
					method: "e_desk.e_desk.doctype.registration_desk.registration_desk.make_sales_invoice",
					frm: frm
				});
			}, __('Create'));
		}
	},

});

frappe.ui.form.on('Registration Desk Item', {
	item(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item) return;

		frappe.call({
			method: "e_desk.e_desk.doctype.registration_desk.registration_desk.get_item_price",
			args: { item_code: row.item },
			callback(r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, 'rate', r.message);
					refresh_row_amount(frm, cdt, cdn);
				}
			}
		});
	},
	qty(frm, cdt, cdn) {
		refresh_row_amount(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		refresh_row_amount(frm, cdt, cdn);
	}
});

function update_item_group(frm) {
	current_item_group = "";
	if (!frm.doc.confer) return;

	frappe.db.get_value('Conference', frm.doc.confer, 'registration_item_group')
		.then(r => {
			current_item_group = (r && r.message && r.message.registration_item_group) || "";
		});
}

function refresh_row_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const amount = flt(row.rate) * flt(row.qty);
	frappe.model.set_value(cdt, cdn, 'amount', amount);
	calculate_totals(frm);
}

function calculate_totals(frm) {
	let total_amount = 0;
	(frm.doc.items || []).forEach(row => {
		total_amount += flt(row.rate) * flt(row.qty);
	});

	frm.set_value('total_amount', total_amount);
}