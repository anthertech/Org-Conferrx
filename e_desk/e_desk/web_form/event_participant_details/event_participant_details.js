// frappe.ready(function() {
    // Retrieve the confer_id from local storage
    // const storedConferId = localStorage.getItem('confer_id');
	

    // if (storedConferId) {
		
	// 			frappe.web_form.doc.parent = storedConferId;
	// 			frappe.web_form.doc.parenttype = 'Confer'; 
	// 			frappe.web_form.doc.parentfield = 'event_participant';
	// 			frappe.web_form.column.doctype='event_participant';
	// 			frappe.web_form.section.doctype='event_participant';
	// 			frappe.web_form.section.doc.docstatus=0
	// 			frappe.web_form.column.doc.docstatus=0
	// 			frappe.web_form.doc.in_view_mode="true"
				


	// 			console.log('Parentttt:', frappe.web_form.doc.parent);  // Debugging
	// 			console.log('Parent tttttttttttttttttttttttttType:', frappe.web_form.doc.parenttype);  // Debugging
	// 			console.log('Parent Field:', frappe.web_form.doc.parentfield); 
	        

    //     frappe.call({
    //         method: 'e_desk.e_desk.web_form.event_participant_details.event_participant_details.form_update',
    //         args: { conf: storedConferId },
    //         callback: function(r) {
    //             if (r.message) {
    //                 if (r.message.event_dict) {

	// 					// frappe.web_form.set_value("parent",storedConferId)
	// 					frappe.web_form.doc.is_new="false"



	// 					console.log(r.message.event_dict,"r.message.event_dictr.message.event_dict");
						
    //                     for (let key in r.message.event_dict) {
    //                         if (r.message.event_dict.hasOwnProperty(key)) {
    //                             frappe.web_form.set_value(key, r.message.event_dict[key]);
    //                         }
	// 						// frappe.web_form.set_value(docstatus, 1);
	// 						// frappe.web_form.doc.docstatus=1
    //                     }
	// 					frappe.web_form.column.docname=r.message.event_dict['name']
	// 					frappe.web_form.section.docname=r.message.event_dict['name']
    //                 }
    //                 if (r.message.confer) {
    //                     const targetElement = document.querySelector('.web-form-title.ellipsis');
    //                     const newDiv = document.createElement('div');
    //                     newDiv.innerHTML = `<h6>Event: ${r.message.confer.name}</h6><span>Start Date: ${r.message.confer.start_date}</span><span>End Date: ${r.message.confer.end_date}</span>`;
    //                     targetElement.appendChild(newDiv);
    //                 }
					
    //             }
    //         }
    //     });
    // }



    // console.log("hello worold......................")


    // const user_email = frappe.session.user;
    // console.log(user_email,"what is this email...............")
    // const storedConferId = localStorage.getItem('confer_id');
    // console.log(storedConferId,"storedConferIdstoredConferId")
    
   
    //    if (user_email &&  ) {
    //     console.log("this is euser gooooot")
    //        frappe.db.get_value('Participant', { email: user_email }, 'name')
    //            .then(r => {
    //             console.log(r,"this r................................");
                
    //                let participant_id = r.message.name;
    //                console.log(participant_id,"participant_id.....")
                   
   
    //                if (participant_id) {
    //                    frappe.web_form.set_value('participant', participant_id);
    //                }
    //            });
    //    }

// });


frappe.ready(function() {
    // console.log("hello world......................");

    // const user_email = frappe.session.user;
    // console.log(user_email, "what is this email...............");

    // // Retrieve the stored conference ID from local storage
    // const storedConferId = localStorage.getItem('confer_id');
    // console.log(storedConferId, "storedConferIdstoredConferId");

    // // Check if the user_email is available
    // if (user_email) {
    //     // Make a call to get the participant ID based on the user's email
    //     frappe.call({
    //         method: "e_desk.e_desk.web_form.event_participant_details.event_participant_details.get_participant_id",
    //         args: {
    //             user_email: user_email
    //         },
    //         callback: function(response) {
    //             console.log("Response:", response);

    //             if (response.message) {
    //                 let participant_id = response.message;
    //                 console.log("Participant ID:", participant_id);

    //                 // Set the participant and event fields in the web form

    //                 // if (participant_id) {
    //                 //     frappe.web_form.set_value('participant', participant_id);
    //                 //     frappe.web_form.set_value('event', storedConferId);
    //                 // }
    //             }
    //         },
    //         error: function(error) {
    //             console.error("Error fetching participant:", error);
    //         }
    //     });
    // }
});
