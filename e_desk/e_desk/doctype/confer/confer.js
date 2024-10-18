// Copyright (c) 2024, sathya and contributors
// For license information, please see license.txt


frappe.ui.form.on('Confer', {
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
