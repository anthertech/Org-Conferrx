# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns= [
		{
			'fieldname': 'participant',
			'fieldtype': 'Link',
			'label': 'Participant',
			'options': 'Participant',
			'width': 200
		},
		{
			'fieldname': 'participant_name',
			'fieldtype': 'Data',
			'label': 'Participant Name',
			'width': 300
		},
		{
			'fieldname': 'registration_no',
			'fieldtype': 'Data',
			'label': 'Registration No',
			'width': 150
		},
		{
			'fieldname': 'subject',
			'fieldtype': 'Data',
			'label': 'Subject',
			'width': 300
		},
		{
			'fieldname': 'session',
			'fieldtype': 'Data',
			'label': 'session',
			'width': 300
		},
	]
	data =[]
	if filters.get("session"):	
		session_list=frappe.get_all("Voting Topic",{'session':filters.get("session")})
		for j in session_list:
			session=frappe.get_doc("Voting Topic",j.name)
			if session.voting:
				for i in session.voting:
					if filters.get("registration_no"):
						frappe.errprint(filters.get("registration_no"))
						participant = frappe.get_all("Participant",{'name':['in',[i.participant]],'reg_no':['like',f'''%{filters.get("registration_no")}%''']},['name','full_name','reg_no'])
					else:
						participant = frappe.get_all("Participant",{'name':['in',[i.participant]]},['name','full_name','reg_no'])
						frappe.errprint(participant)
					for k in participant:
						sub_data = {
							'participant': k.name,
							'participant_name': k.full_name,
							'registration_no': k.reg_no,
							'subject':session.subject,
							'session':session.session,
						}
						data.append(sub_data)
			count = f'<html><b style="font-size:15px">Total Vote Count: </b><b style="color:green; font-size:15px">{session.vote_count or 0} </html>'

	return columns, data, count
