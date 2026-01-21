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
                reqd: 1
            },
            {
                fieldtype: 'Datetime',
                fieldname: 'end_date',
                label: 'End Date',
                reqd: 1
            },
            {
                fieldtype: 'Link',
                fieldname: 'warehouse',
                label: 'Warehouse',
                options: 'Warehouse',
                default: frm.doc.custom_warehouse,
                reqd: 1
            },
            {
                fieldtype: 'Datetime',
                fieldname: 'registration_close_date',
                label: 'Registration Close Date',
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
}
