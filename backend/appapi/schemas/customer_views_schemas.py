from colander import Integer
from colander import Invalid
from colander import Length
from colander import Boolean
from colander import Range
from colander import Regex
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.appapi.schemas.recovery_views_schemas import recaptcha_response
from backend.api_schemas import amount
from backend.api_schemas import FieldStorage
from backend.api_schemas import Recipient
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


def username():
    return SchemaNode(String(), name='username', validator=validate_username)


def name(name='name'):
    return SchemaNode(StrippedString(), name=name, validator=Length(1, 50))


class AddressSchema(Schema):
    name = SchemaNode(StrippedString(), validator=Length(max=50))
    line1 = SchemaNode(StrippedString(), validator=Length(max=50))
    line2 = SchemaNode(StrippedString(), missing='', validator=Length(max=50))
    city = SchemaNode(String(), validator=Length(max=100))
    state = SchemaNode(
        String(), validator=Regex('^[A-Za-z]{2}$', msg='Must be two letters'))
    zip_code = SchemaNode(
        String(), validator=Regex('^[0-9]{5}$', msg='Must be five digits'))
    verified = SchemaNode(String(), missing='')

class SignupSchema(Schema):
    login = SchemaNode(Recipient())
    username = username()

class AddFactorSchema(SignupSchema):
    attempt_path = SchemaNode(StrippedString())
    secret = SchemaNode(String(), validator=Length(max=1000))

class SignupFinishSchema(Schema):
    agreed = SchemaNode(Boolean())
    attempt_path = SchemaNode(StrippedString())
    secret = SchemaNode(String(), validator=Length(max=1000))

class SetSignupDataSchema(Schema):
    attempt_path = SchemaNode(StrippedString())
    first_name = name(name='first_name')
    last_name = name(name='last_name')
    secret = SchemaNode(String(), validator=Length(max=1000))

class AuthUidSchema(Schema):
    factor_id = SchemaNode(StrippedString())
    code = SchemaNode(StrippedString())
    recaptcha_response = recaptcha_response()
    attempt_path = SchemaNode(StrippedString())
    secret = SchemaNode(String(), validator=Length(max=1000))

class RegisterSchema(Schema):
    first_name = name(name='first_name')
    last_name = name(name='last_name')
    username = username()
    profile_id = SchemaNode(String())
    expo_token = SchemaNode(String(), missing='', validator=Length(max=1000))
    os = SchemaNode(String(), missing='', validator=Length(max=100))

class IsCustomerSchema(Schema):
    expected_env = SchemaNode(String())


class SendSchema(Schema):
    amount = amount()
    design_id = SchemaNode(String())
    recipient_id = SchemaNode(String())
    message = SchemaNode(
        StrippedString(), missing='', validator=Length(max=500))


class EditProfileSchema(Schema):
    username = username()
    first_name = name(name='first_name')
    last_name = name(name='last_name')


class HistorySchema(Schema):
    limit = SchemaNode(Integer(), missing=100, validator=Range(min=1))
    offset = SchemaNode(Integer(), missing=0, validator=Range(min=0))


class TransferSchema(Schema):
    transfer_id = SchemaNode(String(), validator=Length(max=100))


class SearchCustomersSchema(Schema):
    query = SchemaNode(String(), validator=Length(max=1000))


class UploadProfileImageSchema(Schema):
    image = SchemaNode(FieldStorage())
