// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Participant", {


	refresh: function(frm) {
        // Check if the current user has the 'E Desk Admin' role
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'User',
                name: frappe.session.user
            },
            callback: function(r) {
                if (r.message && r.message.roles) {
                    let roles = r.message.roles.map(role => role.role);
					let is_admin = roles.includes('E-Desk Admin')
                    frm.set_df_property('status', 'read_only',!is_admin)
                }
            } // Close callback function
        }); // Close frappe.call
    },
	
	get_directions:function(frm){
	
		if (frm.doc.location_url) {
			const mapURL = frm.doc.location_url;
	
			window.open(mapURL);

		} else {
			frappe.msgprint(__('Location URL is required to navigate to the map.'));
		}
	},

    	
	get_directions_church:function(frm){
	
		if (frm.doc.location_url_church) {
			const mapURL = frm.doc.location_url_church;
	
			window.open(mapURL);

		} else {
			frappe.msgprint(__('Location URL is required to navigate to the map.'));
		}
	},

    hotel: function (frm) {
        var selectedHotel = frm.doc.hotel;
        if (selectedHotel) {
            frappe.call({
                method: "e_desk.e_desk.doctype.participant.participant.full_address",
                args: {
                    address: frm.doc.hotel,
                },
                callback: function (search_text) {
                    frm.set_value('hotel_address', search_text.message);
                }
            });
        }
    },

    church_list: function (frm) {
		var selectedchurch = frm.doc.church_list;
		if (selectedchurch) {
			frappe.call({
				method: "e_desk.e_desk.doctype.participant.participant.full_address_church",
				args: {
					address: frm.doc.church_list,
				},
				callback: function (search_text) {
					frm.set_value('church_address', search_text.message);
				}
			});
		}
	}



});
