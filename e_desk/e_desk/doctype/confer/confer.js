// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Confer', {





    // onload: function(frm) {
    //     console.log("on loadadddd")
    //     frappe.call({
    //         method: 'e_desk.e_desk.doctype.confer.confer.get_system_timezone',
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















    refresh: function(frm) {
     
        if (!frm.doc.is_default) {
            frm.add_custom_button(__('Set as Default'), function() { 
        
                frm.set_value('is_default', 1);
                
   
                frm.save().then(() => {
                 
                    frappe.call({
                        method: 'e_desk.e_desk.doctype.confer.confer.update_is_default_for_others',
                        args: {
                            confer_name: frm.doc.name
                        },
                        callback: function(response) {
                            frappe.show_alert({
                                message: __('This Confer has been set as Default and others updated.'),
                                indicator: 'green'
                            });
                        }
                    });
                });
            });
        }
		// else{

		// 	frm.add_custom_button(__('Remove Default event'), function() { 

		// 		frm.set_value('is_default', 0);
		// 		frm.save()
		// 	})
		// }
    }
});
