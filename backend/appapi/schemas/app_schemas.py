from colander import Invalid
from colander import Length
from colander import required
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import RecipientSchema
from backend.api_schemas import StrippedString
import re


def validate_username(node, value):
    if len(value) < 4:
        raise Invalid(node, "Must contain at least 4 characters")
    if len(value) > 20:
        raise Invalid(node, "Must not be longer than 20 characters")
    if value[0].isdigit():
        raise Invalid(node, "Must not start with a number")
    if re.compile(r'^[A-Za-z][A-Za-z0-9\.]{3,19}$').match(value) is None:
        raise Invalid(node, "Can only contain letters, numbers, and periods")


def recipient():
    return SchemaNode(RecipientSchema())


def device_id():
    return SchemaNode(String())


def design_id():
    return SchemaNode(String())


def recaptcha_response(missing=None):
    return SchemaNode(String(), missing=missing)


def name(missing=''):
    return SchemaNode(
        StrippedString(), missing=missing, validator=Length(0, 50))


def username(missing=required):
    return SchemaNode(
        String(),
        missing=missing,
        validator=validate_username)


def expo_token(missing=''):
    return SchemaNode(String(), missing=missing)


class DeviceSchema(Schema):
    device_id = device_id()
