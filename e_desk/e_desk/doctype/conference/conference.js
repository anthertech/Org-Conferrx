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