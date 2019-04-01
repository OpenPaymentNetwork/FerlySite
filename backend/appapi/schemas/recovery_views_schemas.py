from colander import OneOf
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import StrippedString
from backend.appapi.schemas import app_schemas as schemas


class RecoverySchema(Schema):
    device_id = schemas.device_id()
    login = SchemaNode(StrippedString())


class RecoveryCodeSchema(Schema):
    device_id = schemas.device_id()
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    factor_id = SchemaNode(String())
    recaptcha_response = schemas.recaptcha_response()
    attempt_path = SchemaNode(String())
    expo_token = schemas.expo_token()
    os = SchemaNode(String(), missing='')


class AddUIDSchema(Schema):
    device_id = schemas.device_id()
    login = SchemaNode(StrippedString())
    uid_type = SchemaNode(String(), validator=OneOf(['phone', 'email']))


class AddUIDCodeSchema(Schema):
    device_id = schemas.device_id()
    code = SchemaNode(StrippedString())
    secret = SchemaNode(String())
    attempt_id = SchemaNode(String())
    recaptcha_response = schemas.recaptcha_response()
    replace_uid = SchemaNode(String(), missing=None)


class AuthUIDCodeSchema(Schema):
    device_id = schemas.device_id()
    code = SchemaNode(StrippedString())
    factor_id = SchemaNode(String())
