from colander import Email
from colander import Float
from colander import Integer
from colander import Length
from colander import Range
from colander import Regex
from colander import required
from colander import Schema
from colander import SchemaNode
from colander import String


def device_id():
    return SchemaNode(String(), missing=required)


def design_id():
    return SchemaNode(String(), missing=required)


def amount():
    return SchemaNode(Float(), validator=Range(min=0.01), missing=required)


def name(missing=''):
    return SchemaNode(String(), missing=missing, validator=Length(0, 50))


def username(missing=required):
    return SchemaNode(
        String(),
        missing=missing,
        validator=Regex('^[a-zA-Z][a-zA-Z0-9.]{3,19}$'))


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
    expo_token = SchemaNode(String(), missing='')


class DesignSchema(Schema):
    design_id = design_id()


class ContactSchema(Schema):
    email = SchemaNode(String(), missing=required, validator=Email())


class WalletSchema(Schema):
    device_id = device_id()


class SendSchema(Schema):
    amount = amount()
    design_id = design_id()
    device_id = device_id()
    recipient_id = SchemaNode(String(), missing=required)


class PurchaseSchema(Schema):
    amount = amount()
    design_id = design_id()
    device_id = device_id()
    nonce = SchemaNode(String(), missing=required)


class AcceptSchema(Schema):
    offer_id = SchemaNode(String(), missing=required)
    option_id = SchemaNode(String(), missing=required)
    device_id = device_id()


class HistorySchema(Schema):
    device_id = device_id()
    limit = SchemaNode(
        Integer(), title="limit", missing='10', validator=Range(min=0))
    offset = SchemaNode(
        Integer(), title="offset", missing='0', validator=Range(min=0))
