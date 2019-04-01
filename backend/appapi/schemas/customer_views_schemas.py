from colander import Integer
from colander import Length
from colander import Range
from colander import required
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import amount
from backend.api_schemas import FieldStorage
from backend.api_schemas import StrippedString
from backend.appapi.schemas.app_schemas import design_id
from backend.appapi.schemas.app_schemas import device_id
from backend.appapi.schemas.app_schemas import expo_token
from backend.appapi.schemas.app_schemas import name
from backend.appapi.schemas.app_schemas import username


class RegisterSchema(Schema):
    device_id = device_id()
    first_name = name(missing=required)
    last_name = name(missing=required)
    username = username(missing=required)
    expo_token = expo_token()
    os = SchemaNode(String(), missing='')


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


class EditProfileSchema(Schema):
    device_id = device_id()
    username = username(missing=required)
    first_name = name(missing=required)
    last_name = name(missing=required)


class HistorySchema(Schema):
    device_id = device_id()
    limit = SchemaNode(Integer(), missing=100, validator=Range(min=1))
    offset = SchemaNode(Integer(), missing=0, validator=Range(min=0))


class TransferSchema(Schema):
    device_id = device_id()
    transfer_id = SchemaNode(String())


class SearchUsersSchema(Schema):
    device_id = device_id()
    query = SchemaNode(String())


class UploadProfileImageSchema(Schema):
    device_id = device_id()
    image = SchemaNode(FieldStorage())
