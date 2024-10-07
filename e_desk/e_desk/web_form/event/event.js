// frappe.ready(function() {
//     // Bind event to the Participant link field
//     $('input[data-fieldname="participant"]').on('change', function() {
//         var participant_id = $(this).val();
//         if (participant_id) {
//             fetchParticipantData(participant_id);
//         }
//     });

//     // Add fields to the form if not already present
//     addDynamicFields();
// });

// function fetchParticipantData(participant_id) {
//     frappe.call({
//         method: 'frappe.client.get',
//         args: {
//             doctype: 'Participant',
//             name: participant_id
//         },
//         callback: function(r) {
//             if (r.message) {
//                 console.log("Data fetched successfully.");
//                 console.log(r.message, "Participant data");

//                 // Populate fields with data
//                 $('input[data-fieldname="full_name"]').val(r.message.full_name);
//                 $('input[data-fieldname="email"]').val(r.message.email);
//                 $('input[data-fieldname="phone_number"]').val(r.message.phone_number);
//             }
//         }
//     });
// }

// function addDynamicFields() {
//     var formWrapper = $('.form-section'); // Adjust this selector if needed

//     // Check if fields are already added
//     if ($('input[data-fieldname="full_name"]').length === 0) {
//         // Create HTML for new fields
//         var fieldHTML = `
//             <div class="form-group">
//                 <label class="control-label col-sm-4">Full Name</label>
//                 <div class="col-sm-8">
//                     <input type="text" class="form-control" data-fieldname="full_name" placeholder="Full Name">
//                 </div>
//             </div>
//             <div class="form-group">
//                 <label class="control-label col-sm-4">Email</label>
//                 <div class="col-sm-8">
//                     <input type="text" class="form-control" data-fieldname="email" placeholder="Email">
//                 </div>
//             </div>
//             <div class="form-group">
//                 <label class="control-label col-sm-4">Phone Number</label>
//                 <div class="col-sm-8">
//                     <input type="text" class="form-control" data-fieldname="phone_number" placeholder="Phone Number">
//                 </div>
//             </div>
//         `;

//         // Append the new fields to the form
//         formWrapper.append(fieldHTML);
//     }
// }
