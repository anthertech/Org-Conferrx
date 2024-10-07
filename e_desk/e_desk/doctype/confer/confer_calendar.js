
frappe.views.calendar["Confer"] = {
    field_map: {
        "start": "start", 
        "end": "end", 
        "title": "title", 
        "eventColor": "color"
    },
    gantt: true,
    
    get_events_method: "e_desk.e_desk.doctype.event_participant.event_participant.get_confer_agenda_events"
};
