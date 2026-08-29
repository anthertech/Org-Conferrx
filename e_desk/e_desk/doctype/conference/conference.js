// Copyright (c) 2025, Anther Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('Conference', {
	refresh: function (frm) {
		frm.add_custom_button(__("Add Speaker"), function () {
			open_add_speaker_dialog(frm);
		});

        (frm.doc.agenda || []).forEach(row => {
            if (row.conference_programme_agenda && !row.speakers) {
                frappe.call({
                    method: "e_desk.e_desk.doctype.conference.conference.get_speakers_display",
                    args: { cpa_name: row.conference_programme_agenda },
                    callback: function(r) {
                        if (r.message !== undefined) {
                            frappe.model.set_value(row.doctype, row.name, "speakers", r.message);
                            frm.refresh_field("agenda");
							frm.save();
                        }
                    }
                });
            }
        });

		Object.keys(SECTION_FIELD_MAP).forEach((master_fieldname) => {
            set_section_fields(frm, master_fieldname);
        });
	},

	show_personal_information(frm) {
        set_section_fields(frm, "show_personal_information");
    },
    show_additional_info(frm) {
        set_section_fields(frm, "show_additional_info");
    },
    show_contact_details(frm) {
        set_section_fields(frm, "show_contact_details");
    },
    show_medical_informations(frm) {
        set_section_fields(frm, "show_medical_informations");
    },
    show_room_allotment(frm) {
        set_section_fields(frm, "show_room_allotment");
    },
    show_travel_research(frm) {
        set_section_fields(frm, "show_travel_research");
    },
    show_passport_details(frm) {
        set_section_fields(frm, "show_passport_details");
    },
    show_travel_details(frm) {
        set_section_fields(frm, "show_travel_details");
    },
    show_airline_details(frm) {
        set_section_fields(frm, "show_airline_details");
    },
    show_deliberative_sessions(frm) {
        set_section_fields(frm, "show_deliberative_sessions");
    },


    // onload: function(frm) {
    //     console.log("on loadadddd")
    //     frappe.call({
    //         method: 'e_desk.e_desk.doctype.conference.conference.get_system_timezone',
    //         callback: function(r) {
    //             if (r.message) {
    //                 console.log(r.message,"thi sis msg........")
    //                 frm.set_df_property('time_zone', 'options', r.message);
    //             }
    //         }
    //     });
    // },

    before_load: function (frm) {
		let update_tz_options = function () {
			frm.fields_dict.time_zone.set_data(frappe.all_timezones);
		};

		if (!frappe.all_timezones) {
			frappe.call({
				method: "frappe.core.doctype.user.user.get_timezones",
				callback: function (r) {
					frappe.all_timezones = r.message.timezones;
					update_tz_options();
				},
			});
		} else {
			update_tz_options();
		}
	},
	
 
});


frappe.ui.form.on("Conference Agenda", {
    conference_programme_agenda: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.conference_programme_agenda) {
            frappe.model.set_value(cdt, cdn, "speakers", "");
            return;
        }

        frappe.call({
            method: "e_desk.e_desk.doctype.conference.conference.get_speakers_display",
            args: { cpa_name: row.conference_programme_agenda },
            callback: function(r) {
                if (r.message !== undefined) {
                    frappe.model.set_value(cdt, cdn, "speakers", r.message);
					frm.save();
                }
            }
        });
    }
});

const SPEAKER_LINK_FIELDNAME = "speaker";
const SPEAKER_NAME_FIELDNAME = "speaker_name";
const AGENDA_MASTER_DOCTYPE = "Conference Programme Agenda";

function open_add_speaker_dialog(frm) {
	if (!frm.doc.agenda || !frm.doc.agenda.length) {
		frappe.msgprint(__("Please add at least one Program Agenda row first."));
		return;
	}
	if (frm.is_dirty()) {
		frappe.msgprint(__("Please save the Conference before adding speakers."));
		return;
	}
	if (!frm.doc.speaker || !frm.doc.speaker.length) {
		frappe.msgprint(__("Please add speakers to the Conference's Speaker list first."));
		return;
	}

	const row_by_label = {};
	const speaker_name_cache = {};
	frm.doc.speaker.forEach((s) => {
		if (s.speaker) {
			speaker_name_cache[s.speaker] = s.speaker_name || s.speaker;
		}
	});

	const options = frm.doc.agenda.map((row) => {
		const label = `${row.idx}. ${row.program_agenda || "Untitled"}`;
		row_by_label[label] = row;
		return label;
	});

	const dialog = new frappe.ui.Dialog({
		title: __("Add Speakers"),
		fields: [
			{
				fieldname: "agenda_row",
				fieldtype: "Select",
				label: __("Program Agenda"),
				options: options,
				reqd: 1,
				onchange: function () {
					const row = row_by_label[dialog.get_value("agenda_row")];
					prefill_existing_speakers(dialog, row, speaker_name_cache);
				},
			},
			{
				fieldname: "speakers",
				fieldtype: "MultiSelectPills",
				label: __("Speakers"),
				reqd: 1,

				get_data: function (txt) {
					const search = (txt || "").toLowerCase();

					const matches = frm.doc.speaker.filter((s) => {
						const name = (s.speaker_name || "").toLowerCase();
						const id = (s.speaker || "").toLowerCase();
						return name.includes(search) || id.includes(search);
					});

					return matches.map((s) => ({
						value: s.speaker,
						description: s.speaker_name,
					}));
				},
			},
		],

		primary_action_label: __("Save"),

		primary_action: async function (values) {
			const row = row_by_label[values.agenda_row];

			const selected = values.speakers || [];

			const btn = dialog.get_primary_btn();
			btn.prop("disabled", true);

			try {
				const speaker_rows = selected.map((participant) => ({
					[SPEAKER_LINK_FIELDNAME]: participant,
					[SPEAKER_NAME_FIELDNAME]:
						speaker_name_cache[participant] || participant,
				}));

				if (row.conference_programme_agenda) {
					const master = await frappe.db.get_doc(
						AGENDA_MASTER_DOCTYPE,
						row.conference_programme_agenda
					);

					master.speakers = speaker_rows;

					await frappe.call({
						method: "frappe.client.save",
						args: { doc: master },
					});

					frappe.show_alert({ message: __("Speakers updated"), indicator: "green" });
					dialog.hide();
					return;
				}

				const master_doc = {
					doctype: AGENDA_MASTER_DOCTYPE,
					title: `${frm.doc.name}-${row.name}`,
					conference: frm.doc.name,
					programme_agenda_reference: row.name,
					speakers: speaker_rows,
				};

				const response = await frappe.call({
					method: "frappe.client.insert",
					args: { doc: master_doc },
				});

				if (response.message) {
					await frappe.model.set_value(
						"Conference Agenda",
						row.name,
						"conference_programme_agenda",
						response.message.name
					);
					frm.refresh_field("agenda");
					await frm.save();

					frappe.show_alert({ message: __("Speakers added"), indicator: "green" });
					dialog.hide();
				}
			} catch (error) {
				console.error(error);
				frappe.msgprint({
					title: __("Error"),
					message: __("Unable to save speakers. Please check the console for details."),
					indicator: "red",
				});
			} finally {
				btn.prop("disabled", false);
			}
		},
	});

	dialog.show();

	if (options.length === 1) {
		dialog.set_value("agenda_row", options[0]);
		const row = row_by_label[options[0]];
		prefill_existing_speakers(dialog, row, speaker_name_cache);
	}
}

async function prefill_existing_speakers(dialog, row, speaker_name_cache) {
	if (!row || !row.conference_programme_agenda) {
		dialog.set_value("speakers", []);
		return;
	}

	try {
		const doc = await frappe.db.get_doc(
			"Conference Programme Agenda",
			row.conference_programme_agenda
		);

		const existing = (doc.speakers || [])
			.map((s) => {
				if (s[SPEAKER_LINK_FIELDNAME]) {
					speaker_name_cache[s[SPEAKER_LINK_FIELDNAME]] =
						speaker_name_cache[s[SPEAKER_LINK_FIELDNAME]] ||
						s[SPEAKER_NAME_FIELDNAME] ||
						s[SPEAKER_LINK_FIELDNAME];
				}
				return s[SPEAKER_LINK_FIELDNAME];
			})
			.filter(Boolean);

		dialog.set_value("speakers", existing);
	} catch (error) {
		console.error(error);
		dialog.set_value("speakers", []);
	}
}

const SECTION_FIELD_MAP = {
    show_personal_information: [
        "custom_preferred_titless", "prefix", "full_name", "abbr", "gender",
        "profile_photo", "date_of_birth", "custom_youth", "custom_layordained",
        "status", "custom_capacity_", "custom_fax",
        "custom_official_position__designation", "custom_churchorganisation_you_represent",
    ],
    show_additional_info: [
        "id_proof", "id_proof_no", "custom_age_category",
        "company__organization", "gst__pan_no",
    ],
    show_contact_details: [
        "address_title", "address_line_1", "address_line_2", "city", "state",
        "country", "postal_code", "custom_residential_address", "custom_street_or_po",
        "participant_address", "custom_emergency_contact_name", "participant_contact",
        "custom_emergency_contact_email", "custom_contact_number",
    ],
    show_medical_informations: [
        "custom_indigenous_person", "custom_person_with_disability",
        "custom_dietary_specification", "custom_allergies",
    ],
    show_room_allotment: [
        "custom_checkin_date", "custom_number_of_nights",
        "custom_checkout_date", "custom_room_type_and_price_tier",
    ],
    show_travel_research: [
        "custom_your_own_contribution_in_usd", "custom_total_ticket_cost_in_usd",
        "custom_request_for_subsidy_in_usd", "custom_travel_sector",
        "custom_title_of_the_research_paper_", "custom_synopsis_of_the_research_paper",
    ],
    show_passport_details: [
        "custom_first_name_as_per_passport", "custom_last_name_as_per_passport",
        "custom_date_of_expiry", "custom_passport_nationality", "custom_passport_number",
        "custom_country_of_residence", "custom_date_of_issue", "custom_place_of_issue",
        "custom_scan_of_passports_information_page", "custom_visa_entrance",
    ],
    show_travel_details: [
        "mode_of_travel", "flight_no", "departure_time", "arrival_time",
        "custom_arrival_date_and_time", "custom_departure_from",
        "custom_departure_date_and_time",
    ],
    show_airline_details: [
        "custom_airline_arrival", "custom_airline_arrival_date",
        "custom_flight_number_arrival", "custom_airline_departures",
        "custom_airline_departure_date", "custom_flight_number_departure",
    ],
    show_deliberative_sessions: [
        "custom_first_preference_", "custom_second_preference",
        "custom_first_preference", "custom_second_preference_",
    ],
};

function set_section_fields(frm, master_fieldname) {
    const enabled = cint(frm.doc[master_fieldname]);
    const fields = SECTION_FIELD_MAP[master_fieldname] || [];

    fields.forEach((fieldname) => {
        if (!frm.fields_dict[fieldname]) {
            return;
        }

        frm.set_value(fieldname, enabled ? 1 : 0);
        frm.set_df_property(fieldname, "read_only", 1);
    });

    frm.refresh_fields();
}
