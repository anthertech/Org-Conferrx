# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime



def execute(filters=None):
	columns = [   
		{
			'fieldname': 'category',
			'fieldtype': 'Link',
			'label': 'Category',
			'options': 'Category Name',
			'width': 300
		},
		{
			'fieldname': 'participant',
			'fieldtype': 'Link',
			'label': 'Participant',
			'options': 'Participant',
			'width': 250
		},
		{
			'fieldname': 'participant_name',
			'fieldtype': 'Data',
			'label': 'Participant Name',
			'width': 350
		},
		{
			'fieldname': 'attendance_list',
			'fieldtype': 'Data',
			'label': 'Attendance List',
			'width': 300
		},
		{
			'fieldname': 'reg_no',
			'fieldtype': 'Data',
			'label': 'Reg No',
			'width': 250
		},

	]

	data = []
	if filters.get("from_date") and filters.get("to_date") and not filters.get("category"):
		from_date_str = filters.get("from_date")
		to_date_str = filters.get("to_date")
		from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
		to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

		category = frappe.get_all("Category Name")
		attendance_dict = {}
		for i in category:
			if frappe.db.exists('Participant', {'capacity': ['in', i.name]}):
				if filters.get("reg_no"):
					participant_list = frappe.get_all('Participant', {'capacity': ['in', i.name],'reg_no':['like',f'''%{filters.get("reg_no")}%''']})
				else:
					participant_list = frappe.get_all('Participant', {'capacity': ['in', i.name]})
				for h in participant_list:
					participant = frappe.get_doc('Participant', h.name)
					if participant.attendance_list:
						for attendance in participant.attendance_list:
							attendance_date = attendance.get("datetime").date()
							if from_date <= attendance_date <= to_date:
								if i.name not in attendance_dict:
									attendance_dict[i.name] = []
								attendance_dict[i.name].append(attendance)
		for category_name, attendance_list in attendance_dict.items():
			sub_data = {
				'category': category_name,
				'participant': '',
				'participant_name': '',
				'attendance_list': len(attendance_list),
				'indent': 0
			}
			data.append(sub_data)
			for attendance in attendance_list:
				participant = frappe.get_doc('Participant', attendance.parent)
				sub_data = {
					'category': "",
					'participant': participant.name,
					'participant_name': participant.full_name,
					'attendance_list': attendance.datetime,
					'reg_no':participant.reg_no,
					'indent': 1
				}
				data.append(sub_data)
	if filters.get("from_date") and filters.get("to_date") and filters.get("category"):
		from_date_str = filters.get("from_date")
		to_date_str = filters.get("to_date")
		from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
		to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
		i=filters.get("category")
		attendance_dict = {}
		if frappe.db.exists('Participant', {'capacity': ['in', filters.get("category")]}):
			if filters.get("reg_no"):
				participant_list = frappe.get_all('Participant', {'capacity': ['in', filters.get("category")],'reg_no':['like',f'''%{filters.get("reg_no")}%''']})
			else:
				participant_list = frappe.get_all('Participant', {'capacity': ['in', filters.get("category")]})

			for h in participant_list:
				participant = frappe.get_doc('Participant', h.name)
				if participant.attendance_list:
					for attendance in participant.attendance_list:
						attendance_date = attendance.get("datetime").date()
						if from_date <= attendance_date <= to_date:
							if i not in attendance_dict:
								attendance_dict[i] = []
							attendance_dict[i].append(attendance)
		for category_name, attendance_list in attendance_dict.items():
			sub_data = {
				'category': category_name,
				'participant': '',
				'participant_name': '',
				'attendance_list': len(attendance_list),
				'indent': 0
			}
			data.append(sub_data)
			for attendance in attendance_list:
				participant = frappe.get_doc('Participant', attendance.parent)
				sub_data = {
					'category': "",
					'participant': participant.name,
					'participant_name': participant.full_name,
					'attendance_list': attendance.datetime,
					'reg_no':participant.reg_no,
					'indent': 1
				}
				data.append(sub_data)


	return columns, data
