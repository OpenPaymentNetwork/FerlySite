from colander import Integer
from colander import Invalid
from colander import Length
from colander import OneOf
from colander import Range
from colander import required
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import amount
from backend.api_schemas import FieldStorage
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


class DeleteInvitationSchema(Schema):
    device_id = device_id()
    invite_id = SchemaNode(String())


class ExistingInvitationsSchema(Schema):
    device_id = device_id()
    status = SchemaNode(
        String(),
        missing=None,
        validator=OneOf(['pending', 'deleted', 'accepted']))


class InviteSchema(Schema):
    device_id = device_id()
    recipient = recipient()


class RecoverySchema(Schema):
    device_id = device_id()
    login = SchemaNode(StrippedString())


class RecoveryCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    factor_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    attempt_path = SchemaNode(String())
    expo_token = expo_token()
    os = SchemaNode(String(), missing='')


class UIDSchema(Schema):
    device_id = device_id()
    login = SchemaNode(StrippedString())
    uid_type = SchemaNode(String(), validator=OneOf(['phone', 'email']))


class AddUIDCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    attempt_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    replace_uid = SchemaNode(String(), missing=None)


class AuthUIDCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(StrippedString())
    factor_id = SchemaNode(String())


class EditProfileSchema(Schema):
    device_id = device_id()
    username = username(missing=required)
    first_name = name(missing=required)
    last_name = name(missing=required)


class RegisterSchema(Schema):
    device_id = device_id()
    first_name = name(missing=required)
    last_name = name(missing=required)
    username = username(missing=required)
    expo_token = expo_token()
    os = SchemaNode(String(), missing='')


class DesignSchema(Schema):
    design_id = design_id()


class DeviceSchema(Schema):
    device_id = device_id()


class IsUserSchema(Schema):
    device_id = device_id()
    expected_env = SchemaNode(String(), missing='staging')


class SendSchema(Schema):
    amount = amount()
    design_id = design_id()
    device_id = device_id()
    recipient_id = SchemaNode(String())
    message = SchemaNode(
        StrippedString(), missing='', validator=Length(max=500))


class PurchaseSchema(Schema):
    amount = amount(minimum=0.50)
    design_id = design_id()
    device_id = device_id()
    source_id = SchemaNode(String())


class DeleteSourceSchema(Schema):
    device_id = device_id()
    source_id = SchemaNode(String())


class HistorySchema(Schema):
    device_id = device_id()
    limit = SchemaNode(Integer(), missing=100, validator=Range(min=1))
    offset = SchemaNode(Integer(), missing=0, validator=Range(min=0))


class TransferSchema(Schema):
    device_id = device_id()
    transfer_id = SchemaNode(String())


class SearchMarketSchema(Schema):
    query = SchemaNode(String())


class SearchUsersSchema(Schema):
    device_id = device_id()
    query = SchemaNode(String())


class UploadProfileImageSchema(Schema):
    device_id = device_id()
    image = SchemaNode(FieldStorage())
