// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Registration Desk', {

	setup: function(frm) {

		frm.set_query('confer', function(doc, cdt, cdn) {
            return {
                filters: [
                    ['start_date', '>=', frappe.datetime.get_today()] // Only show upcoming or ongoing conferences
                ]
            };
        });


        // Set query for the participant link field inside the Participant child table
        frm.set_query('participant_id', 'participant', function(doc, cdt, cdn) {
			if (frm.doc.confer){
            return {

					query: 'e_desk.e_desk.doctype.registration_desk.registration_desk.event_participant_filter',
					filters: {
						conference: frm.doc.confer
					}	
				};
			}
			else{
				frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Select the confer for fetching participant')
                });
				
			}
        });
    },










	refresh:function(frm){
		
		let imgList = [];
		(frm.doc.participant || []).forEach(row => {
			console.log(row,"this is row")
			imgList.push({'img': row.profile_img})
		});

		let imgHTML = ''

		imgList.forEach(img => {
			if (img.img) {
				imgHTML += `
				<div>
					<img src='${img.img}' alt='IMG' height="100" width="100">
					<br>
					<br>
				</div>
				`
			}
		});

		frm.get_field("profile_preview").$wrapper.html(imgHTML);


		let qrList = [];
		(frm.doc.participant || []).forEach(row => {
			qrList.push({'img': row.qr_img})
		});

		let qrHTML = ''

		qrList.forEach(img => {
			if (img.img) {
				qrHTML += `
				<div>
					<img src='${img.img}' alt='IMG' height="100" width="100">
					<br>
					<br>
				</div>
				`
			}
		});

		frm.get_field("qr_preview").$wrapper.html(qrHTML);
		

	},




	
	participant_profile:function(frm){
		if(frm.doc.part_profile){
			let $profileimg = `
				<img
				class="sign"
				src=${frm.doc.part_profile} 
				/>
				`
				frm.get_field("profile_preview").$wrapper.html($profileimg);
		}
	},
});





