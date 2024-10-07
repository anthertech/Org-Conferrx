frappe.ready(function() {



    const confer_id = localStorage.getItem('confer_id')
    if (confer_id){
        frappe.web_form.set_value('event', confer_id)
    }

    // Bind the onchange event to the e_mail field
    $('input[data-fieldname="e_mail"]').on('change', function() {
        let email = $(this).val();
        console.log(email,"email........")
     
        // if (email) {
      

        //     frappe.call({
        //         method: "e_desk.e_desk.web_form.event_participant_registration.event_participant_registration.check_user_exists",
        //         args: {
        //             email: email
        //         },
        //         callback: function(response) {
        //             console.log(response,"response..............");
                    
                    
        //             let user = response.message;
        //             console.log(user,"user exist,,,,,,,,,,,,")

        //             if (user) {
        //                 // Email exists, redirect to login
                  
        //                 frappe.msgprint({
        //                     title: __('Error'),
        //                     indicator: 'red',
        //                     message: __('This email is already registered. Please proceed with registration through the Existing User option')
        //                 });

		// 				setTimeout(function() {
        //                     window.location.href = '/home';
        //                 }, 3000); 
                     
        //             } 
                 
        //         }
        //     });
        // }



    });
});
