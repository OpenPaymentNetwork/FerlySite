
from colander import Length
from colander import OneOf
from colander import SchemaNode
from colander import String
from backend.api_schemas import StrippedString
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema


def recaptcha_response(missing=None):
    return SchemaNode(String(), missing=missing, validator=Length(max=1000))


class RecoverySchema(CustomerDeviceSchema):
    login = SchemaNode(StrippedString(), validator=Length(max=100))


class RecoveryCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString(), validator=Length(max=100))
    secret = SchemaNode(String(), validator=Length(max=1000))
    factor_id = SchemaNode(String(), validator=Length(max=100))
    recaptcha_response = recaptcha_response()
    attempt_path = SchemaNode(String(), validator=Length(max=200))
    expo_token = SchemaNode(String(), missing='', validator=Length(max=1000))
    os = SchemaNode(String(), missing='', validator=Length(max=100))


class AddUIDSchema(CustomerDeviceSchema):
    login = SchemaNode(StrippedString(), validator=Length(max=100))
    uid_type = SchemaNode(String(), validator=OneOf(['phone', 'email']))


class AddUIDCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString(), validator=Length(max=100))
    secret = SchemaNode(String(), validator=Length(max=1000))
    attempt_id = SchemaNode(String(), validator=Length(max=100))
    recaptcha_response = recaptcha_response()
    replace_uid = SchemaNode(
        String(), missing=None, validator=Length(max=1000))


class AuthUIDCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString(), validator=Length(max=100))
    factor_id = SchemaNode(String(), validator=Length(max=100))
