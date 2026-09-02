frappe.ui.form.on('Project', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Event'), function () {
                open_event_dialog(frm);
            }, __('Actions'));
        }
    }
});

function open_event_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __('Create Event'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'event_title',
                label: 'Event Title',
                default: frm.doc.project_name || frm.doc.name,
                reqd: 1
            },
            {
                fieldtype: 'Data',
                fieldname: 'abbreviation',
                label: 'Abbreviation',
                reqd: 1
            },
            {
                fieldtype: 'Datetime',
                fieldname: 'start_date',
                label: 'Start Date',
                default: frm.doc.expected_start_date,
                reqd: 1
            },
            {
                fieldtype: 'Datetime',
                fieldname: 'end_date',
                label: 'End Date',
                default: frm.doc.expected_end_date,
                reqd: 1
            },
            {
                fieldtype: 'Check',
                fieldname: 'is_wh_required',
                label: 'Is Warehouse Required',
                onchange() {
                    const required = d.get_value("is_wh_required");

                    d.set_df_property("default_wh", "hidden", !required);

                    d.set_df_property("default_wh", "reqd", required);

                    if (!required) {
                        d.set_value("default_wh", "");
                    }
                }
            },
            {
                fieldtype: 'Link',
                fieldname: 'default_wh',
                options: 'Warehouse',
                label: 'Default Warehouse',
                hidden: 1,
                reqd: 0
            },
            {
                fieldtype: 'Datetime',
                fieldname: 'registration_close_date',
                label: 'Registration Close Date',
                reqd: 1
            },
            {
                fieldtype: 'Autocomplete',
                fieldname: 'time_zone',
                label: 'Time Zone',
                reqd: 1
            }
        ],
        primary_action_label: __('Create Event'),
        primary_action(values) {
            frappe.call({
                method: "e_desk.e_desk.api.project.create_event_from_project",
                args: {
                    project: frm.doc.name,
                    data: values
                },
                freeze: true,
                freeze_message: __("Creating Event..."),
                callback(r) {
                    if (r.message) {
                        d.hide();
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Event created successfully'),
                            indicator: 'green'
                        });
                        frappe.set_route('Form', 'Conference', r.message);
                    }
                }
            });
        }
    });

    d.show();

    // Populate Time Zone dropdown with all timezones
    let set_tz_data = function () {
        d.fields_dict.time_zone.set_data(frappe.all_timezones);
    };

    if (!frappe.all_timezones) {
        frappe.call({
            method: "frappe.core.doctype.user.user.get_timezones",
            callback: function (r) {
                frappe.all_timezones = r.message.timezones;
                set_tz_data();
            },
        });
    } else {
        set_tz_data();
    }
}
