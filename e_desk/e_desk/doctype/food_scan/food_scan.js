// Copyright (c) 2024, anthertech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Food Scan', {
	setup: function(frm) {
        frm.disable_save();
    },
	submit: function(frm) {
		var name = JSON.parse(frm.doc.scan_qr).name;
		frm.set_value("scan_qr","")
				frappe.call({
				method: "e_desk.e_desk.doctype.participant.participant.validate_food",
				args: {
					doc: name,
				},
				callback:function(r){
					if (r.message){
						frappe.show_alert({message:"Food Scanned Sucessfully", indicator:'green'});
						var item = cur_frm.add_child("scanned_list");
						frappe.model.set_value(item.doctype, item.name, "participant", r.message);
						frappe.model.set_value(item.doctype, item.name, "date_time", frappe.datetime.now_datetime());
						cur_frm.refresh_field('scanned_list');
						cur_frm.save();
					}
					
				}

			})
		},
		}
		)
	
