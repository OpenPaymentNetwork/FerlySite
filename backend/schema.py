from colander import Email
from colander import Float
from colander import Integer
from colander import Invalid
from colander import Length
from colander import null
from colander import OneOf
from colander import Range
from colander import required
from colander import Schema
from colander import SchemaNode
from colander import SchemaType
from colander import String
import cgi
import phonenumbers
import re


phone_detect_re = re.compile(r'^[(+\s]*[0-9]')

_email_validator = Email()


class RecipientSchema(String):

    def deserialize(self, node, cstruct):
        value = String.deserialize(self, node, cstruct)
        if not value:
            return null

        value = value.strip()
        if not value:
            return null

        if '@' in value:
            try:
                _email_validator(node, value)
            except Invalid:
                raise Invalid(node, 'Invalid email address')
            else:
                return value
        elif phone_detect_re.match(value):
            try:
                pn = phonenumbers.parse(value, 'US')
            except Exception:
                raise Invalid(node, msg='Invalid phone number.')
            else:
                if phonenumbers.is_valid_number(pn):
                    e164value = phonenumbers.format_number(
                        pn, phonenumbers.PhoneNumberFormat.E164)
                    return e164value
                else:
                    raise Invalid(node, msg='Invalid phone number')
        else:
            raise Invalid(node, msg='Must be a valid email or phone number')


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


def amount():
    return SchemaNode(Float(), validator=Range(min=0.01))


def recaptcha_response(missing=None):
    return SchemaNode(String(), missing=missing)


def name(missing=''):
    return SchemaNode(String(), missing=missing, validator=Length(0, 50))


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
    login = SchemaNode(String())


class RecoveryCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(String())
    secret = SchemaNode(String())
    factor_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    attempt_path = SchemaNode(String())
    expo_token = expo_token()
    os = SchemaNode(String(), missing='')


class UIDSchema(Schema):
    device_id = device_id()
    login = SchemaNode(String())
    uid_type = SchemaNode(String(), validator=OneOf(['phone', 'email']))


class AddUIDCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(String())
    secret = SchemaNode(String())
    attempt_id = SchemaNode(String())
    recaptcha_response = recaptcha_response()
    replace_uid = SchemaNode(String(), missing=None)


class AuthUIDCodeSchema(Schema):
    device_id = device_id()
    code = SchemaNode(String())
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
    os = SchemaNode(String())


class DesignSchema(Schema):
    design_id = design_id()


class ContactSchema(Schema):
    email = SchemaNode(String(), validator=Email())


class DeviceSchema(Schema):
    device_id = device_id()


class SendSchema(Schema):
    amount = amount()
    design_id = design_id()
    device_id = device_id()
    recipient_id = SchemaNode(String(), missing=required)
    message = SchemaNode(String(), missing='', validator=Length(max=500))


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
        Integer(), title="limit", missing='10', validator=Range(min=1))
    offset = SchemaNode(
        Integer(), title="offset", missing='0', validator=Range(min=0))


class TransferSchema(Schema):
    device_id = device_id()
    transfer_id = SchemaNode(String())


class SearchMarketSchema(Schema):
    query = SchemaNode(String())


class SearchUsersSchema(Schema):
    device_id = device_id()
    query = SchemaNode(String())


class FieldStorage(SchemaType):
    def serialize(self, node, appstruct):
        return appstruct

    def deserialize(self, node, cstruct):
        if not isinstance(cstruct, cgi.FieldStorage):
            raise Invalid(node, '%r is not of type FieldStorage' % cstruct)
        return cstruct


class UploadProfileImageSchema(Schema):
    device_id = device_id()
    image = SchemaNode(FieldStorage())
