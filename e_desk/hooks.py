from . import __version__ as app_version

app_name = "e_desk"
app_title = "E Desk"
app_publisher = "sathya"
app_description = "E Desk"
app_email = "sathya@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/e_desk/css/e_desk.css"
# app_include_js = "e_desk/e_desk/doctype/participant/participant.js"

# include js, css files in header of web template
# web_include_css = "/assets/e_desk/css/e_desk.css"
# web_include_js = "/assets/e_desk/js/e_desk.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "e_desk/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"Participant" : "e_desk/doctype/participant/participant.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }




fixtures = [
  
    {"dt": "Custom Field", "filters": [["module", "=", "E Desk"]],
    "prefix": "e_desk_custom_fields"}
]









# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "e_desk.utils.jinja_methods",
#	"filters": "e_desk.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "e_desk.install.before_install"
# after_install = "e_desk.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "e_desk.uninstall.before_uninstall"
# after_uninstall = "e_desk.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "e_desk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	# "File": "e_desk.e_desk.utils.py.permissions.file.get_file_permission",
    "Participant":"e_desk.e_desk.utils.py.permissions.file.participant_query_conditions",
    "Event Participant": "e_desk.e_desk.doctype.event_participant.event_participant.event_has_permission"
    
}
# permission_query_conditions = {
# 	"Conf Programme Attendee": "e_desk.e_desk.doctype.event_participant.event_participant.has_permission",
# }
#
has_permission = {
	"Participant": "e_desk.e_desk.doctype.event_participant.event_participant.participant_has_permission",
    "Event Participant":"e_desk.e_desk.doctype.event_participant.event_participant.event_participant_has_permission",
    # "Confer":"e_desk.e_desk.doctype.event_participant.event_participant.confer_has_permission"
    
   
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Address": {
		"validate": "e_desk.e_desk.utils.py.address.address_link",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"e_desk.tasks.all"
#	],
#	"daily": [
#		"e_desk.tasks.daily"
#	],
#	"hourly": [
#		"e_desk.tasks.hourly"
#	],
#	"weekly": [
#		"e_desk.tasks.weekly"
#	],
#	"monthly": [
#		"e_desk.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "e_desk.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "e_desk.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "e_desk.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["e_desk.utils.before_request"]
# after_request = ["e_desk.utils.after_request"]

# Job Events
# ----------
# before_job = ["e_desk.utils.before_job"]
# after_job = ["e_desk.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"e_desk.auth.validate"
# ]
