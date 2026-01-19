// Copyright (c) 2026, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Exhibitor", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Exhibitor', {
    refresh(frm) {
        frm.set_query('stall', () => {
            return {
                filters: {
                    item_group: 'Stall',
                    disabled: 0
                }
            };
        });
    }
});
