from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from json.decoder import JSONDecodeError
from logging import info
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from typing import List

from eNMS.forms import form_classes, form_templates
from eNMS.database import delete, factory, fetch, fetch_all, fetch_all_visible
from eNMS.dispatcher.administration_dispatcher import AdministrationDispatcher
from eNMS.dispatcher.automation_dispatcher import AutomationDispatcher
from eNMS.dispatcher.import_export_dispatcher import ImportExportDispatcher
from eNMS.dispatcher.inventory_dispatcher import InventoryDispatcher
from eNMS.models import classes
from eNMS.modules import db
from eNMS.properties import (
    default_diagrams_properties,
    table_fixed_columns,
    table_properties,
    type_to_diagram_properties,
)


class Dispatcher(
    AutomationDispatcher,
    AdministrationDispatcher,
    ImportExportDispatcher,
    InventoryDispatcher,
):
    def dashboard(self) -> dict:
        on_going = {
            "Running services": len(
                [
                    service
                    for service in fetch_all("Service")
                    if service.status == "Running"
                ]
            ),
            "Running workflows": len(
                [
                    workflow
                    for workflow in fetch_all("Workflow")
                    if workflow.status == "Running"
                ]
            ),
            "Scheduled tasks": len(
                [task for task in fetch_all("Task") if task.status == "Active"]
            ),
        }
        return dict(
            properties=type_to_diagram_properties,
            default_properties=default_diagrams_properties,
            counters={
                **{cls: len(fetch_all_visible(cls)) for cls in classes},
                **on_going,
            },
        )

    def delete(self, cls: str, instance_id: int) -> dict:
        instance = delete(cls, id=instance_id)
        info(f'{current_user.name}: DELETE {cls} {instance["name"]} ({id})')
        return instance

    def filtering(self, table: str) -> dict:
        model = classes.get(table, classes["Device"])
        properties = table_properties[table]
        if table in ("configuration", "device"):
            properties.append("current_configuration")
        try:
            order_property = properties[int(request.args["order[0][column]"])]
        except IndexError:
            order_property = "name"
        order = getattr(getattr(model, order_property), request.args["order[0][dir]"])()
        constraints = []
        for property in properties:
            value = request.args.get(f"form[{property}]")
            if value:
                constraints.append(getattr(model, property).contains(value))
        result = db.session.query(model).filter(and_(*constraints)).order_by(order)
        if table in ("device", "link", "configuration"):
            pools = [int(id) for id in request.args.getlist("form[pools][]")]
            if pools:
                result = result.filter(model.pools.any(classes["pool"].id.in_(pools)))
        return {
            "jsonify": True,
            "draw": int(request.args["draw"]),
            "recordsTotal": len(model.query.all()),
            "recordsFiltered": len(result.all()),
            "data": [
                [getattr(obj, property) for property in properties]
                + obj.generate_row(table)
                for obj in result.limit(int(request.args["length"]))
                .offset(int(request.args["start"]))
                .all()
            ],
        }

    def form(self, form_type: str) -> dict:
        return dict(
            form=form_classes.get(form_type, FlaskForm)(request.form),
            form_type=form_type,
            template=f"forms/{form_templates.get(form_type, form_type + '_form')}",
        )

    def get_all(self, cls: str) -> List[dict]:
        info(f"{current_user.name}: GET ALL {cls}")
        return [instance.get_properties() for instance in fetch_all_visible(cls)]

    def get(self, cls: str, id: str) -> dict:
        instance = fetch(cls, id=id)
        info(f"{current_user.name}: GET {cls} {instance.name} ({id})")
        return instance.serialized

    def table(self, table_type: str) -> dict:
        return dict(
            properties=table_properties[table_type],
            fixed_columns=table_fixed_columns[table_type],
            type=table_type,
            template="pages/table",
        )

    def update(self, cls: str) -> dict:
        try:
            instance = factory(cls, **request.form)
            info(
                f"{current_user.name}: UPDATE {cls} " f"{instance.name} ({instance.id})"
            )
            return instance.serialized
        except JSONDecodeError:
            return {"error": "Invalid JSON syntax (JSON field)"}
        except IntegrityError:
            return {"error": "An object with the same name already exists"}


dispatcher = Dispatcher()
