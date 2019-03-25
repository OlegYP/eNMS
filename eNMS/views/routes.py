from flask import current_app as app, request
from typing import Union

from eNMS.base.functions import fetch, fetch_all, get, get_one, post
from eNMS.base.properties import subtype_sizes, link_subtype_to_color
from eNMS.inventory.forms import (
    AddDevice,
    AddLink,
    AddPoolForm,
    DeviceAutomationForm,
    GottyConnectionForm,
)
from eNMS.views import bp, styles
from eNMS.views.forms import ViewForm


@get(bp, "/<view_type>_view", "View")
def view(view_type: str) -> dict:
    parameters = get_one("Parameters").serialized
    return dict(
        add_pool_form=AddPoolForm(request.form),
        template=f"geographical_view.html",
        parameters=parameters,
        google_earth_form=GoogleEarthForm(request.form),
        add_device_form=AddDevice(request.form),
        add_link_form=AddLink(request.form),
        device_automation_form=DeviceAutomationForm(request.form),
        subtype_sizes=subtype_sizes,
        gotty_connection_form=GottyConnectionForm(request.form),
        link_colors=link_subtype_to_color,
        view="2D",
        view_type=view_type,
        view_form=ViewForm(request.form),
    )


@post(bp, "/get_logs/<int:device_id>", "View")
def get_logs(device_id: int) -> Union[str, bool]:
    device_logs = [
        log.content
        for log in fetch_all("Log")
        if log.source == fetch("Device", id=device_id).ip_address
    ]
    return "\n".join(device_logs) or True
