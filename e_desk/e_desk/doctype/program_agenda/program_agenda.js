// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Program Agenda', {
	validate: function(frm) {

        var child_table = frm.doc.agenda_details || [];
        child_table.sort(function(a, b) {
            return frappe.datetime.get_diff(a.from_time, b.from_time);
        });


		for (var i = 0; i < child_table.length - 1; i++) {
            var current_row = child_table[i];
            var next_row = child_table[i + 1];

            if (current_row['to_time'] >= next_row['from_time']) {
                frappe.msgprint(__('Time intervals should not overlap.'));
                frappe.validated = false;
                return;
            }
        }



    },
    refresh: function (frm) {
        var agendaDetails = frm.doc.agenda_details || [];
        if (frm.doc.agenda_details) {
            var agendaTable = `<style>
            .body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            h1 {
                color: #333;
            }
            table {
                width: 100%;
                margin: 20px auto;
                border-collapse: collapse;
                background-color: #fff;
            }
            th, td {
                padding: 15px;
                text-align: left;
            }
            th:nth-child(1), td:nth-child(1) {
                width: 30%; 
            }
            th:nth-child(2), td:nth-child(2) {
                width: 70%; 
            }
            th {
                background-color: #333;
                color: #fff;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #ddd;
            }
            </style>`;
    
            var find = false;
    
            for (var i = 0; i < agendaDetails.length; i++) {
                var row = agendaDetails[i];
                if (agendaDetails[0].from_time) {
                    if (!find) {
                        agendaTable += ' <div class="body"> <table border="1"><tr><th>Time</th><th>Event</th></tr>';
                        find = true;
                    }
                    agendaTable += '<tr>';
                    agendaTable += '<td>' + row.from_time + ' - ' + row.to_time + '</td>';
                    agendaTable += '<td>' + row.description + '</td>';
                    agendaTable += '</tr>';
                }
            }
    
            agendaTable += '</div></table>';
            frm.get_field("agenda_list").$wrapper.html(agendaTable);
        } else {
            frm.get_field("agenda_list").$wrapper.html('');
        }
    }
    
    
});
