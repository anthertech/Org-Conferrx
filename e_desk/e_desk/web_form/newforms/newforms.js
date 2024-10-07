// frappe.ready(function() {
// 	// bind events here
// })

frappe.ready(function() {
    console.log("hello world......................");

    const user_email = frappe.session.user;
    console.log(user_email, "what is this email...............");

    // Retrieve the stored conference ID from local storage
    const storedConferId = localStorage.getItem('confer_id');
    console.log(storedConferId, "storedConferIdstoredConferId");

    // Check if the user_email is available
    if (user_email) {
        // Make a call to get the participant ID based on the user's email
        frappe.call({
            method: "e_desk.e_desk.web_form.event_participant_details.event_participant_details.get_participant_id",
            args: {
                user_email: user_email
            },
            callback: function(response) {
                console.log("Response:", response);

                if (response.message) {
                    let participant_id = response.message;
                    console.log("Participant ID:", participant_id);

                    // Set the participant and event fields in the web form
                    
                    if (participant_id) {
                        frappe.web_form.set_value('participant', participant_id);
                        frappe.web_form.set_value('event', storedConferId);
                    }
                }
            },
            error: function(error) {
                console.error("Error fetching participant:", error);
            }
        });
    }
});