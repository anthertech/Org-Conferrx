// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Conference', {





    // onload: function(frm) {
    //     console.log("on loadadddd")
    //     frappe.call({
    //         method: 'e_desk.e_desk.doctype.conference.conference.get_system_timezone',
    //         callback: function(r) {
    //             if (r.message) {
    //                 console.log(r.message,"thi sis msg........")
    //                 frm.set_df_property('time_zone', 'options', r.message);
    //             }
    //         }
    //     });
    // },

    before_load: function (frm) {
		let update_tz_options = function () {
			frm.fields_dict.time_zone.set_data(frappe.all_timezones);
		};

		if (!frappe.all_timezones) {
			frappe.call({
				method: "frappe.core.doctype.user.user.get_timezones",
				callback: function (r) {
					frappe.all_timezones = r.message.timezones;
					update_tz_options();
				},
			});
		} else {
			update_tz_options();
		}
	},
	
 
});
