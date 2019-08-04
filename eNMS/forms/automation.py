from wtforms import BooleanField, HiddenField, IntegerField, SelectField, StringField
from wtforms.widgets import TextArea

from eNMS.controller import controller
from eNMS.forms import BaseForm
from eNMS.forms.fields import (
    DictField,
    MultipleInstanceField,
    NoValidationSelectField,
    NoValidationSelectMultipleField,
    PasswordSubstitutionField,
    SubstitutionField,
)


class JobForm(BaseForm):
    template = "job"
    form_type = HiddenField(default="job")
    id = HiddenField()
    type = StringField("Service Type")
    name = StringField("Name")
    description = StringField("Description")
    python_query = StringField("Python Query")
    query_property_type = SelectField(
        "Query Property Type", choices=(("name", "Name"), ("ip_address", "IP address"))
    )
    devices = MultipleInstanceField("Devices", instance_type="Device")
    pools = MultipleInstanceField("Pools", instance_type="Pool")
    waiting_time = IntegerField("Waiting time (in seconds)", default=0)
    send_notification = BooleanField("Send a notification")
    send_notification_method = SelectField(
        "Notification Method",
        choices=(
            ("mail_feedback_notification", "Mail"),
            ("slack_feedback_notification", "Slack"),
            ("mattermost_feedback_notification", "Mattermost"),
        ),
    )
    notification_header = StringField(widget=TextArea(), render_kw={"rows": 5})
    include_link_in_summary = BooleanField("Include Result Link in Summary")
    display_only_failed_nodes = BooleanField("Display only Failed Devices")
    mail_recipient = StringField("Mail Recipients (separated by comma)")
    number_of_retries = IntegerField("Number of retries", default=0)
    time_between_retries = IntegerField("Time between retries (in seconds)", default=10)
    start_new_connection = BooleanField("Start New Connection")
    skip = BooleanField("Skip")
    skip_python_query = StringField("Skip (Python Query)")
    vendor = StringField("Vendor")
    operating_system = StringField("Operating System")
    shape = SelectField(
        "Shape",
        choices=(
            ("box", "Box"),
            ("circle", "Circle"),
            ("square", "Square"),
            ("diamond", "Diamond"),
            ("triangle", "Triangle"),
            ("ellipse", "Ellipse"),
            ("database", "Database"),
        ),
    )
    size = IntegerField("Size", default=40)
    color = StringField("Color", default="#D2E5FF")
    initial_payload = DictField()

    def validate(self) -> bool:
        valid_form = super().validate()
        no_recipient_error = (
            self.send_notification.data
            and self.send_notification_method.data == "mail_feedback_notification"
            and not self.mail_recipient.data
            and not controller.mail_recipients
        )
        if no_recipient_error:
            self.mail_recipient.errors.append(
                "Please add at least one recipient for the mail notification."
            )
        return valid_form and not no_recipient_error


class RunForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="run")
    id = HiddenField()


class ServiceForm(JobForm):
    form_type = HiddenField(default="service")
    credentials = SelectField(
        "Credentials",
        choices=(
            ("device", "Device Credentials"),
            ("user", "User Credentials"),
            ("custom", "Custom Credentials"),
        ),
    )
    custom_username = SubstitutionField("Custom Username")
    custom_password = PasswordSubstitutionField("Custom Password")
    multiprocessing = BooleanField("Multiprocessing")
    max_processes = IntegerField("Maximum number of processes", default=50)


class WorkflowForm(JobForm):
    form_type = HiddenField(default="workflow")
    use_workflow_targets = BooleanField("Use Workflow Targets")
    start_jobs = MultipleInstanceField("Start Jobs", instance_type="Job")
    payload_version = NoValidationSelectField("Payload Version", choices=())
    payloads_to_exclude = NoValidationSelectMultipleField(
        "Payloads to Include", choices=()
    )

    def validate(self) -> bool:
        valid_form = super().validate()
        no_start_jobs_error = not self.start_jobs.data
        if no_start_jobs_error:
            self.start_jobs.errors.append(
                "Please select at least one job as start of the workflow."
            )
        return valid_form and not no_start_jobs_error


class ResultsForm(BaseForm):
    template = "results"
    form_type = HiddenField(default="results")
    compare = BooleanField(default=False)
    view_type = SelectField(
        "View", choices=(("view", "Display as JSON"), ("text", "Display as text"))
    )
    runtime = NoValidationSelectField("Version", choices=())
    runtime_compare = NoValidationSelectField("Version", choices=())


class ServiceResultsForm(ResultsForm):
    form_type = HiddenField(default="service_results")
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())


class WorkflowResultsForm(ResultsForm):
    form_type = HiddenField(default="workflow_results")
    workflow_device = NoValidationSelectField("Device", choices=())
    workflow_device_compare = NoValidationSelectField("Device", choices=())
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())
    job = NoValidationSelectField("Job", choices=())
    job_compare = NoValidationSelectField("Job", choices=())


class DeviceResultsForm(ResultsForm):
    form_type = HiddenField(default="device_results")


class RunResultsForm(ResultsForm):
    form_type = HiddenField(default="run_results")
    device = NoValidationSelectField("Device", choices=())
    device_compare = NoValidationSelectField("Device", choices=())


class AddJobsForm(BaseForm):
    template = "base"
    action = "addJobsToWorkflow"
    form_type = HiddenField(default="add_jobs")
    jobs = MultipleInstanceField("Add jobs", instance_type="Job")


class ServiceTableForm(BaseForm):
    form_type = HiddenField(default="service_table")
    services = SelectField(choices=())
