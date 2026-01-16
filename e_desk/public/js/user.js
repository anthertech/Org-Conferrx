frappe.ui.form.on('User', {
	refresh(frm) {
		load_connections(frm);

		if (frm.doc.custom_qr) {
            frm.fields_dict.custom_qr_preview.$wrapper.html(
                `<div style="text-align:left">
                    <img src="${frm.doc.custom_qr}" style="width:130px !important;">
                 </div>`
            );
        }

		if (frm.is_new() || !frm.doc.email) return;

		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Participant',
				filters: { e_mail: frm.doc.email },
				fields: ['event']
			},
			callback(r) {
				if (!r.message?.length) {
					frm.set_df_property('list_of_events', 'options',
						'<p class="text-muted">No events found</p>');
					return;
				}

				const event_names = r.message.map(p => p.event).filter(Boolean);

				frappe.call({
					method: 'frappe.client.get_list',
					args: {
						doctype: 'Conference',
						filters: { name: ['in', event_names] },
						fields: ['name', 'start_date']
					},
					callback(res) {
						let grouped = {};

						(res.message || []).forEach(e => {
							if (!e.start_date) return;
							const year = new Date(e.start_date).getFullYear();
							grouped[year] ??= [];
							grouped[year].push(e);
						});

						let html = '<div class="timeline">';
						Object.keys(grouped).sort((a, b) => b - a).forEach(year => {
							html += `<h4>${year}</h4><ul>`;
							grouped[year]
								.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
								.forEach(e => {
									html += `<li><b>${e.name}</b> — ${
										frappe.datetime.str_to_user(e.start_date)
									}</li>`;
								});
							html += '</ul>';
						});
						html += '</div>';

						frm.set_df_property('custom_event_list', 'options', html);
						frm.refresh_field('custom_event_list');
					}
				});
			}
		});

        
		
	},
	onload(frm){
		if (frm.doc.custom_qr) {
            frm.fields_dict.custom_qr_preview.$wrapper.html(
                `<div style="text-align:left">
                    <img src="${frm.doc.custom_qr}" style="width:130px !important;">
                 </div>`
            );
        }
	},

	custom_scan_qr(frm) {
		if (!frm.doc.custom_scan_qr || !frm.doc.email) return;

		frappe.call({
			method: "e_desk.e_desk.doctype.participant.participant.connection_doc",
			args: {
				scanned_user: frm.doc.custom_scan_qr, // QR value
				email: frm.doc.email                  // current user
			},
			callback(r) {
				if (r.message?.status === "created") {
					load_connections(frm);
					frappe.show_alert("Connection added");
				} else if (r.message?.status === "exists") {
					frappe.msgprint("Already connected");
				}
				frm.set_value("custom_scan_qr", "");
			}
		});
	}

});

function load_connections(frm) {
	frappe.call({
		method: "e_desk.e_desk.doctype.participant.participant.connection_details",
		args: { email: frm.doc.email },
		callback(r) {
			const field = frm.get_field("custom_address_html");
			field.$wrapper.empty();

			if (!r.message || !r.message.length) {
				field.$wrapper.html("<p>No connections</p>");
				return;
			}

			let html = `<div style="display:flex;flex-wrap:wrap;">`;

			r.message.forEach(c => {
				html += `
					<div style="border:1px solid #ddd;margin:8px;padding:12px;
								border-radius:8px;display:flex;">
						${c.profile_photo
							? `<img src="${c.profile_photo}" width="100"
								   style="border-radius:50%;margin-right:10px;">`
							: `<div style="width:100px;background:#eee;
										 border-radius:50%;margin-right:10px;"></div>`}
						<div>
							<b>${c.full_name}</b><br>
							${c.business_category || ""}<br>
							${c.event || ""}<br>
							${c.email}<br>
							${c.phone || ""}
						</div>
					</div>`;
			});

			html += "</div>";
			field.$wrapper.html(html);
		}
	});
}
