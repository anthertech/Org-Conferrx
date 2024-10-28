// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Participant', {


	setup: function(frm) {  // Alternatively, use refresh instead of setup
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
                    console.log(r.message, "this is message");
                    frm.set_value('event', r.message[0].name);
                }
            }
        });
    },


	
		submit: function(frm) {
			// Parse the scanned QR data to get the Participant name (or ID)
			try {
				var scan_data = JSON.parse(frm.doc.scan_qr).name;  // Assuming QR contains JSON data
				console.log(scan_data, "data.");
				console.log(frm.doc.e_mail,"this is doc name")
	
					if (scan_data) {
						// Call the backend to fetch the participant details
						frappe.call({
							method: "e_desk.e_desk.doctype.participant.participant.connection_doc",
							args: {
								doc_name: scan_data,
								email:frm.doc.e_mail
						},
						callback: function(r) {
							if (r.message) {
								console.log(r.message, "this is message");
				
							} else {
								frappe.msgprint("No participant details found for the scanned QR.");
							}
						}
					});
				}
				 else {
					frappe.msgprint("Invalid QR code scanned.");
				}
			} catch (e) {
				console.error("Error parsing QR data: ", e);
				frappe.msgprint("Failed to process the scanned QR code.");
			}
		

		},


		
			

	//Create button for converting the participant to volunteer
	refresh: function(frm) {
		var hasPermission = frappe.user.has_role('Volunteer'); 
		if (!frm.is_new()){
			toggleEditFields(frm, false); 
			frm.add_custom_button(__('Editable'), function() {
				toggleEditFields(frm, true); 
			  });}
		
			if (hasPermission) {
				frm.add_custom_button(__('Volunteer'), function() {
					
					let d = new frappe.ui.Dialog({
						title: 'Enter details',
						fields: [
							{
								label: 'Confer List',
								fieldname: 'confer',
								fieldtype: 'Link',
								options: 'Confer',
								reqd: 1 ,
								get_query: function() {
									return {
										query: "e_desk.e_desk.utils.role.get_filtered_confer",
										filters: {
											participant: frm.doc.name,
											 // Pass the participant name
										}
									};
								}
							}
						],
						primary_action_label: 'Submit',
						primary_action(values) {    
								frappe.call({
									method: "e_desk.e_desk.utils.role.update_event_participant_role",
									args: {
										participant: frm.doc.name,
										confer: values.confer,
										role_name:'Volunteer'
									},
									callback: function() {
										frappe.msgprint("Volunteer Created Successfully");
										d.hide(); 
									}
								});
						}
					});
					d.show();
				}, __("Create"));
			}

		let qrHTML = ''
		
			if (frm.doc.qr) {
					
				qrHTML += `
				<div>
					<img src='${frm.doc.qr}' alt='IMG' height="100" width="100">
					<br>
					<br>
				</div>
				`
			}
		

		frm.get_field("qr_preview").$wrapper.html(qrHTML);


		if (!frm.is_new()) {

			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Event Participant',
					filters: {
						'participant': frm.doc.name
					},
					fields: ['name', 'event']  // Adjust fields as needed
				},
				callback: function(r) {
					if (r.message) {
						let html_content = "<ul>";
						r.message.forEach(event => {
							html_content += `<li>${event.event}</li>`;
						});
						html_content += "</ul>";
						frm.set_df_property('list_of_events', 'options', html_content);
						frm.refresh_field('list_of_events');
					}
				}
			});
		}
		

		if (!frm.is_new()) {
			frappe.call({
				method: "e_desk.e_desk.doctype.participant.participant.connection_details",
				args: {
					email:frm.doc.e_mail
				},
				callback: function(response) {
					if (response.message) {
						// Clear the existing HTML field content
						frm.get_field("address_html").$wrapper.empty();
	
						// Loop through each connection and append as card
						response.message.forEach(function(connection) {

							if (!frm.get_field("address_html").$wrapper.find('.card-container').length) {
								frm.get_field("address_html").$wrapper.append('<div class="card-container" style="display: flex; flex-wrap: wrap; justify-content: flex-start;"></div>');
							}
							
							let card_html = `
								<div class="card" style="margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; display: flex; align-items: center; background-color: #fff; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); flex: 1 1 calc(33% - 20px); min-width: 250px; max-width: 300px;">
									${connection.profile_photo ? 
									`<img src="${connection.profile_photo}" alt="Profile Photo" style="border-radius: 50%; width: 70px; height: 70px; margin-right: 15px;">` : 
									`<div style="width: 70px; height: 70px; margin-right: 15px; background-color: #eee; border-radius: 50%;"></div>`}
									<div style="flex-grow: 1;">
										<div style="font-weight: bold; font-size: 1.2em; color: #333;">${connection.full_name}</div>
											<div style="color: #777; font-style: italic;">${connection.business_category}</div>
												<div style="color: #555;">${connection.event}</div>
										<div style="color: #555;">${connection.email}</div>
										<div style="color: #555;">${connection.phone}</div>
									
									</div>
								</div>
							`;

// Append the card to the card container
frm.get_field("address_html").$wrapper.find('.card-container').append(card_html);


						
						});
					}
				}
			});
		}





	},


}

);

function toggleEditFields(frm, isEditable) {
	var user= 'mathew@gmail.com'
    var fieldnames = Object.keys(frm.fields_dict);
	console.log(fieldnames,"this is field names...........")
    for (var i = 0; i < fieldnames.length; i++) {
        var fieldname = fieldnames[i];
		if(frappe.session.user != user){
			if (frm.fields_dict[fieldname].df.fieldtype !== 'Section Break' &&
				frm.fields_dict[fieldname].df.fieldtype !== 'Column Break' &&
				isEditable?!frm.fields_dict[fieldname].df.reqd:true )
				{
				frm.toggle_enable(fieldname, isEditable);
        }}
		else{
			if (frm.fields_dict[fieldname].df.fieldtype !== 'Section Break' &&
				frm.fields_dict[fieldname].df.fieldtype !== 'Column Break')
				{
				frm.toggle_enable(fieldname, isEditable);
        }
		}
    }
}
