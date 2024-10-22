// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Registration Desk', {
	custom_submit: function(frm) {
		try {
			// Parse the scanned QR data to get the Participant name (or ID)
			var scan_data = JSON.parse(frm.doc.custom_scan_qr).name;  // Assuming QR contains JSON data
			console.log(scan_data, "data.");
		

			if (scan_data && frm.doc.confer) {
				// Call the backend to fetch the participant details
				frappe.call({
					method: "e_desk.e_desk.doctype.registration_desk.registration_desk.registration_details",
					args: {
						doc: scan_data,   // Participant ID or Name from QR
						confer: frm.doc.confer  // Confer (Event) ID
					},
					callback: function(r) {
						if (r.message) {
							console.log(r.message,"this is messageee..")

							frm.set_value('custom_scan_qr',"");
							frm.set_value('participant_id',r.message.name);
							frm.set_value('participant_name', r.message.full_name);
							frm.set_value('part_profile', r.message.profile_photo);
							frm.set_value('qr_profile', r.message.qr);
							frm.set_value('business_category',r.message.business_category)
							frm.set_value('chapter',r.message.chapter)
							frm.set_value('role',r.message.role)

							// Display the profile image in the profile_preview field
							if (r.message.profile_photo) {
								let imgHTML = `
									<div>
										<img src="${frm.doc.part_profile}" alt="Profile Image" height="100" width="100">
									</div>`;
								frm.get_field("profile_preview").$wrapper.html(imgHTML);
							}

							// Display the QR code in the qr_preview field	
							if (r.message.qr) {
								console.log("qrrr,,,reached here...............")
								console.log(frm.doc.qr_profile,"this is form qr")
								let qrHTML = `
									<div>
										<img src="${frm.doc.qr_profile}" alt="QR Code" height="100" width="100">
									</div>`;
								frm.get_field("qr_preview").$wrapper.html(qrHTML);
							}
						}
					
					}
				});
			} else {
				frappe.msgprint(__('Scan data or conference is missing.'));
			}
		} catch (error) {
			frappe.msgprint(__('Failed to parse QR code. Please check the QR data format.'));
			console.error(error);
		}
	},

	onload: function(frm) {
    
        frm.set_query('confer', function() {
            return {
                filters: {
                    is_default: 1
                }
            };
        });

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Confer',
                fields: ['name'],
                filters: {
                    is_default: 1
                }
            },
            callback: function(r) {
                if (r.message && r.message.length === 1) {
                    frm.set_value('confer', r.message[0].name);
                }
            } 
        });
    },

	
		

});







// 	refresh:function(frm){
		

// 		let imgHTML = ''

// 		imgList.forEach(img => {
// 			if (img.img) {
// 				imgHTML += `
// 				<div>
// 					<img src='${img.img}' alt='IMG' height="100" width="100">
// 					<br>
// 					<br>
// 				</div>
// 				`
// 			}
// 		});

// 		frm.get_field("profile_preview").$wrapper.html(imgHTML);



// 		let qrHTML = ''

// 		qrList.forEach(img => {
// 			if (img.img) {
// 				qrHTML += `
// 				<div>
// 					<img src='${img.img}' alt='IMG' height="100" width="100">
// 					<br>
// 					<br>
// 				</div>
// 				`
// 			}
// 		});

// 		frm.get_field("qr_preview").$wrapper.html(qrHTML);
		

// 	},




	
// 	participant_profile:function(frm){
// 		if(frm.doc.part_profile){
// 			let $profileimg = `
// 				<img
// 				class="sign"
// 				src=${frm.doc.part_profile} 
// 				/>
// 				`
// 				frm.get_field("profile_preview").$wrapper.html($profileimg);
// 		}
// 	},
// });





