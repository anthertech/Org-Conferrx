frappe.views.calendar["Confer"] = {
	field_map: {
		start: "agenda.start_date",
		end: "agenda.end_date",
		id: "name",
		title: "agenda.program_agenda",
		allDay: "allDay",
		progress: "progress",
	},
	gantt: true,
	get_events_method: "frappe.desk.calendar.get_events",
};


