// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Participant', {
	refresh(frm) {
        if (frm.doc.custom_qr_image) {
            frm.fields_dict.qr_preview.$wrapper.html(
                `<div style="text-align:left">
                    <img src="${frm.doc.custom_qr_image}" style="width:130px !important;">
                 </div>`
            );
        }

        apply_meal_rules(frm);
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
        apply_customer_rule(frm)
        frm.trigger('sync_qr_from_user');
	},
	event(frm) {
		apply_meal_rules(frm);
	},
	contact(frm) {
		load_contact_html(frm);
	},
	address(frm) {
		load_address_html(frm);
	},
    
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
    if (!frm.doc.event) return;

    frappe.db.get_value('Conference', frm.doc.event, 'has_meal')
        .then(r => {
            const has_meal = r.message && r.message.has_meal;

            if (!has_meal) {
                frm.set_df_property('meal_included', 'hidden', 1);
                frm.set_df_property('meal_preference', 'hidden', 1);
                frm.set_value('meal_included', 0);
                return;
            }
            frappe.db.get_value('Conference', frm.doc.event, 'meal_access')
                .then(r2 => {
                    const meal_access = r2.message && r2.message.meal_access;

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

function apply_customer_rule(frm) {
    if (!frm.doc.event) return;

    frappe.db.get_value('Conference', frm.doc.event, 'create_customer_on_participant_creation')
        .then(r => {
            const has_create_customer = r.message && r.message.create_customer_on_participant_creation;

            if (!has_create_customer) {
                frm.set_df_property('customer', 'hidden', 1);
                return;
            }
        });
}

function addSpeakerButton(frm) {
    if (!frm.doc.event_role) return;

    if (frm.doc.event_role === "Speaker") {
        frm.add_custom_button(__('Remove Speaker'), () => {
            toggleSpeaker(frm);
        }, __('Actions'));
    } else if (frm.doc.event_role === "Participant") {
        frm.add_custom_button(__('Make Speaker'), () => {
            toggleSpeaker(frm);
        }, __('Actions'));
    }
}

function toggleSpeaker(frm) {
    frappe.call({
        method: "e_desk.e_desk.doctype.participant.participant.toggle_event_speaker",
        args: { participant: frm.doc.name },
        callback() {
            frm.reload_doc();
        }
    });
}



function addVolunteerButton(frm) {
    if (!frm.doc.event_role) return;

    if (frm.doc.event_role === "Volunteer") {
        frm.add_custom_button(__('Remove Volunteer'), () => {
            toggleVolunteer(frm);
        }, __('Actions'));
    } else if (frm.doc.event_role === "Participant") {
        frm.add_custom_button(__('Make Volunteer'), () => {
            toggleVolunteer(frm);
        }, __('Actions'));
    }
}
function toggleVolunteer(frm) {
    frappe.call({
        method: "e_desk.e_desk.doctype.participant.participant.toggle_event_volunteer",
        args: { participant: frm.doc.name },
        callback() {
            frm.reload_doc();
        }
    });
}



function add_view_links(frm) {
    if (frm.is_new() || !frm.doc.event) return;

    // ---------------- Sponsor ----------------
    frappe.db.get_value(
        'Sponsor',
        {
            participant: frm.doc.name,
            event: frm.doc.event
        },
        'name'
    ).then(r => {
        if (r?.message?.name) {
            frm.add_custom_button(__('Sponsor'), () => {
                frappe.set_route('Form', 'Sponsor', r.message.name);
            }, __('View'));
        }
    });

    // ---------------- Exhibitor ----------------
    frappe.db.get_value('Conference', frm.doc.event, 'event_has_exhibitors')
        .then(r => {
            const event_has_exhibitors = r.message && r.message.event_has_exhibitors;
            if (!event_has_exhibitors) return;

            frappe.db.get_value(
                'Exhibitor',
                {
                    participant: frm.doc.name,
                    event: frm.doc.event
                },
                'name'
            ).then(r => {
                if (r?.message?.name) {
                    frm.add_custom_button(__('Exhibitor'), () => {
                        frappe.set_route('Form', 'Exhibitor', r.message.name);
                    }, __('View'));
                }
            });
        });

    // ---------------- User ----------------
    if (frm.doc.user) {
        frm.add_custom_button(__('User'), () => {
            frappe.set_route('Form', 'User', frm.doc.user);
        }, __('View'));
    }

    // ---------------- Hotel ----------------
    frappe.db.get_value(
        'Lodging',
        { participant: frm.doc.name },
        'name'
    ).then(r => {
        if (r?.message?.name) {
            frm.add_custom_button(__('Lodging'), () => {
                frappe.set_route('Form', 'Lodging', r.message.name);
            }, __('View'));
        }
    });
}
