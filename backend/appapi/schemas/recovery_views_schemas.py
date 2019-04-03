from colander import OneOf
from colander import SchemaNode
from colander import String
from backend.api_schemas import StrippedString
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema


def recaptcha_response(missing=None):
    return SchemaNode(String(), missing=missing)


class RecoverySchema(CustomerDeviceSchema):
    login = SchemaNode(StrippedString())


class RecoveryCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    factor_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    attempt_path = SchemaNode(String())
    expo_token = SchemaNode(String(), missing='')
    os = SchemaNode(String(), missing='')


class AddUIDSchema(CustomerDeviceSchema):
    login = SchemaNode(StrippedString())
    uid_type = SchemaNode(String(), validator=OneOf(['phone', 'email']))


class AddUIDCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    attempt_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    replace_uid = SchemaNode(String(), missing=None)


class AuthUIDCodeSchema(CustomerDeviceSchema):
    code = SchemaNode(StrippedString())
    factor_id = SchemaNode(String())
