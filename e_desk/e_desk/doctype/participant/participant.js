// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Participant', {
	refresh(frm) {
		if (frm.is_new()) return;
	
		if (
			frappe.user.has_role('System Manager') ||
			frappe.user.has_role('E-Desk Admin')
		) {
			addVolunteerButton(frm);
			addSpeakerButton(frm);
			
		}
	
		load_contact_html(frm);
		load_address_html(frm);
		add_view_links(frm);
	},
	onload(frm) {
		if (frm.doc.event) {
			apply_meal_rules(frm);
		}
	},
	event(frm) {
		apply_meal_rules(frm);
	},
	contact(frm) {
		load_contact_html(frm);
	},
	address(frm) {
		load_address_html(frm);
	}
});

function load_contact_html(frm) {
    if (!frm.doc.participant_contact) {
        frm.get_field("contact_html").$wrapper.html(
        );
        return;
    }
    frappe.call({
        method: "e_desk.e_desk.doctype.participant.participant.get_contact_html",
        args: {
            contact_name: frm.doc.participant_contact
        },
        callback: function (r) {
            if (r.message) {
                frm.get_field("contact_html").$wrapper.html(r.message);
            }
        }
    });
}

function load_address_html(frm) {
	if (!frm.doc.participant_address) {
		frm.get_field("address_html").$wrapper.html("");
		return;
	}
	frappe.call({
		method: "e_desk.e_desk.doctype.participant.participant.get_address_html",
		args: {
			address_name: frm.doc.participant_address
		},
		callback: function (r) {
			if (r.message) {
				frm.get_field("address_html").$wrapper.html(r.message);
			}
		}
	});
}
function apply_meal_rules(frm) {
    frappe.db.get_single_value('Conference Settings', 'has_meal')
        .then(has_meal => {

            if (!has_meal) {
                frm.set_df_property('meal_included', 'hidden', 1);
                frm.set_df_property('meal_preference', 'hidden', 1);
                frm.set_value('meal_included', 0);
                return;
            }
            frappe.db.get_single_value('Conference Settings', 'meal_access')
                .then(meal_access => {

                    frm.set_df_property('meal_included', 'hidden', 0);
                    frm.set_df_property('meal_preference', 'hidden', 0);

                    if (meal_access === 'Free for All Participants') {
                        frm.set_value('meal_included', 1);
                        frm.set_df_property('meal_included', 'read_only', 1);
                    } else {
                        frm.set_df_property('meal_included', 'read_only', 0);
                    }
                });
        });
}


function addSpeakerButton(frm) {
    if (!frm.doc.event) return;
    const label = frm.doc.speaker ? __('Remove Speaker') : __('Make Speaker');
    frm.add_custom_button(label, () => {
        frappe.call({
            method: "e_desk.e_desk.doctype.participant.participant.update_event_speaker",
            args: {
                participant: frm.doc.name,
            },
            callback() {
                frappe.msgprint(__('Speaker status updated successfully'));
                frm.reload_doc();
            }
        });
    }, __('Actions'));
}


function addVolunteerButton(frm) {
    if (!frm.doc.event) return;
    const label = frm.doc.volunteer ? __('Remove Volunteer') : __('Make Volunteer');
    frm.add_custom_button(label, () => {
        frappe.call({
            method: "e_desk.e_desk.doctype.participant.participant.update_event_volunteer",
            args: {
                participant: frm.doc.name,
                role_name: "Volunteer"
            },
            callback() {
                frappe.msgprint(__('Volunteer role updated successfully'));
                frm.reload_doc();
            }
        });
    }, __('Actions'));
}



function add_view_links(frm) {
    if (!frm.doc.event || frm.is_new()) return;
    frappe.db.get_value(
        'Sponsor',
        {
            participant: frm.doc.name,
            event: frm.doc.event
        },
        'name'
    ).then(r => {
        if (r && r.message) {
            frm.add_custom_button(__('Sponsor'), () => {
                frappe.set_route('Form', 'Sponsor', r.message.name);
            }, __('View'));
        }
    });
    frappe.db.get_single_value('Conference Settings', 'event_has_exhibitors')
        .then(event_has_exhibitors => {
            if (!event_has_exhibitors) return;

            frappe.db.get_value(
                'Exhibitor',
                {
                    participant: frm.doc.name,
                    event: frm.doc.event
                },
                'name'
            ).then(r => {
                if (r && r.message) {
                    frm.add_custom_button(__('Exhibitor'), () => {
                        frappe.set_route('Form', 'Exhibitor', r.message.name);
                    }, __('View'));
                }
            });
        });
    if (frm.doc.user) {
        frm.add_custom_button(__('User'), () => {
            frappe.set_route('Form', 'User', frm.doc.user);
        }, __('View'));
    }
}
