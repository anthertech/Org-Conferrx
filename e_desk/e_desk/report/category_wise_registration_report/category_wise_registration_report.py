# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = [   
		{
			'fieldname': 'category',
			'fieldtype': 'Link',
			'label': 'Category',
			'options': 'Category Name',
			'width': 250
		},
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
			'width': 350
		},
		{
			'fieldname': 'reg_no',
			'fieldtype': 'Data',
			'label': 'Reg No',
			'width': 250
		},
	]
	data = []
	if filters.get("category"):
		if filters.get("reg_no"):
			participants = frappe.get_all('Participant', {'capacity': ['in',filters.get("category")], 'status': "Registered",'reg_no':['like',f'''%{filters.get("reg_no")}%''']})
		else:
			participants = frappe.get_all('Participant', {'capacity': ['in',filters.get("category")], 'status': "Registered"})

		if participants:
			sub_data = {
				'category': filters.get("category"),
				'participants': ''
			}
			data.append(sub_data)
			category_participants = []
			for j in participants:
				participant = frappe.get_doc('Participant', j.name)
				category_participants.append({
					'participant': participant.name,
					'participant_name': participant.full_name,
					'reg_no':participant.reg_no
				})
				for k in category_participants:
					sub_data = {
					'category': '',
					'participant': k['participant'],
					'participant_name':k['participant_name'],
					'reg_no':k['reg_no'],
					'indent': 1  
				}
				data.append(sub_data)

	else:
		categories = frappe.get_all("Category Name")
		for i in categories:
			if filters.get("reg_no"):
				participants = frappe.get_all('Participant', {'capacity': ['in', i.name], 'status': "Registered",'reg_no':['like',f'''%{filters.get("reg_no")}%''']})
			else:
				participants = frappe.get_all('Participant', {'capacity': ['in', i.name], 'status': "Registered"})
			if participants:
				sub_data = {
					'category': i.name,
					'participants': ''
				}
				data.append(sub_data)
				category_participants = []
				for j in participants:
					participant = frappe.get_doc('Participant', j.name)
					category_participants.append({
						'participant': participant.name,
						'participant_name': participant.full_name,
						'reg_no':participant.reg_no

					})
					for k in category_participants:
						sub_data = {
						'category': '',
						'participant': k['participant'],
						'participant_name':k['participant_name'],
						'reg_no':k['reg_no'],
						'indent': 1  
					}
					data.append(sub_data)


	return columns, data
