import frappe

def execute(filters=None):
	columns = [   
		{
			'fieldname': 'participant',
			'fieldtype': 'Link',
			'label': 'Participant',
			'options': 'Participant',
			'width': 300
		},
		{
			'fieldname': 'participant_name',
			'fieldtype': 'Data',
			'label': 'Participant Name',
			'width': 400
		},
		{
			'fieldname': 'registration_no',
			'fieldtype': 'Data',
			'label': 'Registration No',
			'width': 200
		},
		{
			'fieldname': 'scan_date',
			'fieldtype': 'Data',
			'label': 'Scan Date Time',
			'width': 300
		},
	]

	data = []
	party = {}  
	if filters.get("from_date") and filters.get("to_date"):	
		food_scan = frappe.get_all("Food Scanning", filters={"datetime": ["between", [filters.get("from_date"), filters.get("to_date")]]}, fields=['parent', 'datetime'],group_by='datetime')
		if filters.get("registration_no"):
			participant = frappe.get_all("Participant",{'name':['in',[a.parent for a in food_scan]],'reg_no':['like',f'''%{filters.get("registration_no")}%''']},['name','full_name','reg_no'])
		else:
			participant = frappe.get_all("Participant",{'name':['in',[a.parent for a in food_scan]]},['name','full_name','reg_no'])
		for i in participant:
			if i.name not in party:
				party[i.name] = {
					'participant_name': i.full_name,
					'reg_no':i.reg_no,
					'scan_dates': []
				}
			party[i.name]['scan_dates'].extend([b.datetime.strftime('%d-%m-%y %H:%M:%S') for b in frappe.get_all("Food Scanning", filters={"datetime": ["between", [filters.get("from_date"), filters.get("to_date")]],'parent':i.name}, fields=['parent', 'datetime'],group_by='datetime')])  

		participant_count = 0

		for participant_id, participant_data in party.items():
			sub_data = {
				'participant': participant_id,
				'participant_name': participant_data['participant_name'],
				'scan_date': len(participant_data['scan_dates']),
				'registration_no':participant_data['reg_no'],
				'indent': 0
			}
			data.append(sub_data)
			participant_count += 1

			count = f'<html><b style="font-size:15px">Participant Count: </b><b style="color:green; font-size:15px">{participant_count or ""} </html>'
			for k in participant_data['scan_dates']:
				sub_data = {
					'participant': '',
					'participant_name': '',
					'scan_date': k,
					'indent': 1
				}
				data.append(sub_data)
			

	return columns, data, count
