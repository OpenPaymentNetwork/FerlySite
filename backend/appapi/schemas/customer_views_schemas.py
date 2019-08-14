from colander import Integer
from colander import Invalid
from colander import Length
from colander import Range
from colander import Regex
from colander import SchemaNode
from colander import String
from backend.api_schemas import amount
from backend.api_schemas import FieldStorage
from backend.api_schemas import StrippedString
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema
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


def username():
    return SchemaNode(String(), name='username', validator=validate_username)


def name(name='name'):
    return SchemaNode(StrippedString(), name=name, validator=Length(1, 50))


class AddressSchema(CustomerDeviceSchema):
    name = SchemaNode(StrippedString(), validator=Length(max=50))
    line1 = SchemaNode(StrippedString(), validator=Length(max=50))
    line2 = SchemaNode(StrippedString(), missing='', validator=Length(max=50))
    city = SchemaNode(String(), validator=Length(max=100))
    state = SchemaNode(
        String(), validator=Regex('^[A-Za-z]{2}$', msg='Must be two letters'))
    zip_code = SchemaNode(
        String(), validator=Regex('^[0-9]{5}$', msg='Must be five digits'))


class RegisterSchema(CustomerDeviceSchema):
    first_name = name(name='first_name')
    last_name = name(name='last_name')
    username = username()
    expo_token = SchemaNode(String(), missing='', validator=Length(max=1000))
    os = SchemaNode(String(), missing='', validator=Length(max=100))


class IsCustomerSchema(CustomerDeviceSchema):
    expected_env = SchemaNode(String())


class SendSchema(CustomerDeviceSchema):
    amount = amount()
    design_id = SchemaNode(String())
    recipient_id = SchemaNode(String())
    message = SchemaNode(
        StrippedString(), missing='', validator=Length(max=500))


class EditProfileSchema(CustomerDeviceSchema):
    username = username()
    first_name = name(name='first_name')
    last_name = name(name='last_name')


class HistorySchema(CustomerDeviceSchema):
    limit = SchemaNode(Integer(), missing=100, validator=Range(min=1))
    offset = SchemaNode(Integer(), missing=0, validator=Range(min=0))


class TransferSchema(CustomerDeviceSchema):
    transfer_id = SchemaNode(String(), validator=Length(max=100))


class SearchCustomersSchema(CustomerDeviceSchema):
    query = SchemaNode(String(), validator=Length(max=1000))


class UploadProfileImageSchema(CustomerDeviceSchema):
    image = SchemaNode(FieldStorage())
