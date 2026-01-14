// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Registration Desk', {

	scan_qr: function(frm) {
        if (frm.doc.scan_qr) {
            frm.events.submit(frm);
        }
    },
	scan_qr(frm) {
        if (!frm.doc.scan_qr || !frm.doc.confer) return;

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



	refresh:function(frm){

		if (frm.doc.part_profile) {
			let imgHTML = `
				<div>
					<img src="${frm.doc.part_profile}" alt="Profile Image" height="100" width="100">
				</div>`;
			frm.get_field("profile_preview").$wrapper.html(imgHTML);
		}

		// Display the QR code in the qr_preview field	
		if (frm.doc.qr_profile) {
			console.log("qrrr,,,reached here...............")
			console.log(frm.doc.qr_profile,"this is form qr")
			let qrHTML = `
				<div>
					<img src="${frm.doc.qr_profile}" alt="QR Code" height="100" width="100">
				</div>`;
			frm.get_field("qr_preview").$wrapper.html(qrHTML);
		}

		
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





