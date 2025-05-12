// Copyright (c) 2024, anthertech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel', {
	refresh: function(frm) {
		if (frm.doc.latitude && frm.doc.longitude) {
			const map = frm.get_field('location').map;
			const marker = L.marker([frm.doc.latitude, frm.doc.longitude]).addTo(map);
	  
			marker.bindPopup(frm.doc.hotel).openPopup();
		  }
		frm.set_query('address', function(doc) {
			return {
				filters: {
					'link_doctype': 'Hotel',
					'link_name': doc.name
				}
			}
		})
	},
	get_directions:function(frm){
	
		if (frm.doc.location_url) {
			const mapURL = frm.doc.location_url;
	
			window.open(mapURL);

		} else {
			frappe.msgprint(__('Location URL is required to navigate to the map.'));
		}
	},
  });
