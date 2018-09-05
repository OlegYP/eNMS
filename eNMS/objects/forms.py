from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    PasswordField,
    SelectMultipleField,
    SelectField,
    TextField
)
from wtforms.validators import optional

from eNMS.base.properties import (
    link_public_properties,
    link_subtypes,
    node_public_properties,
    node_subtypes
)


class AddObjectForm(FlaskForm):
    name = TextField('Name')
    description = TextField('Description')
    location = TextField('Location')
    vendor = TextField('Vendor')

# nodes can be added to the database either one by one via the AddNode
# form, or all at once by importing an Excel or a CSV file.


class AddNode(AddObjectForm):
    node_types = [subtype for subtype in node_subtypes.items()]
    type = SelectField('Type', choices=node_types)
    ip_address = TextField('IP address', [optional()])
    operating_system = TextField('Operating System', [optional()])
    os_version = TextField('OS version', [optional()])
    longitude = FloatField('Longitude', default=0.)
    latitude = FloatField('Latitude', default=0.)
    secret_password = PasswordField('Secret password')


class AddLink(AddObjectForm):
    link_types = [subtype for subtype in link_subtypes.items()]
    type = SelectField('Type', choices=link_types)
    source = SelectField('Source', choices=())
    destination = SelectField('Destination', choices=())


def configure_form(cls):
    cls.node_properties = node_public_properties
    cls.link_properties = link_public_properties
    for property in node_public_properties:
        setattr(cls, 'node_' + property, TextField(property))
        setattr(cls, 'node_' + property + '_regex', BooleanField('Regex'))
    for property in link_public_properties:
        setattr(cls, 'link_' + property, TextField(property))
        setattr(cls, 'link_' + property + '_regex', BooleanField('Regex'))
    return cls


@configure_form
class AddPoolForm(FlaskForm):
    name = TextField('Name')
    description = TextField('Description')


class PoolObjectsForm(FlaskForm):
    nodes = SelectMultipleField('Nodes', choices=())
    links = SelectMultipleField('Links', choices=())
