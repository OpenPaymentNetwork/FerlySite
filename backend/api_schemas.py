from colander import Email
from colander import Decimal
from colander import Invalid
from colander import null
from colander import Range
from colander import SchemaNode
from colander import SchemaType
from colander import String
import cgi
import decimal
import phonenumbers
import re

phone_detect_re = re.compile(r'^[(+\s]*[0-9]')

_email_validator = Email()


def amount(minimum=0.01):
    return SchemaNode(
        Decimal(quant='0.01', rounding=decimal.ROUND_HALF_UP),
        validator=Range(
            min=decimal.Decimal(str(minimum)),
            min_err='${:.2f} is the minimum'.format(minimum)))


class StrippedString(String):
    """A regular string with whitespace stripped from the ends"""
    def deserialize(self, node, cstruct):
        value = String.deserialize(self, node, cstruct)
        if not value:
            return null
        value = value.strip()
        if not value:
            return null
        return value


class RecipientSchema(StrippedString):

    def deserialize(self, node, cstruct):
        value = StrippedString.deserialize(self, node, cstruct)
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


class FieldStorage(SchemaType):
    def serialize(self, node, appstruct):
        return appstruct

    def deserialize(self, node, cstruct):
        if not isinstance(cstruct, cgi.FieldStorage):
            raise Invalid(node, '%r is not of type FieldStorage' % cstruct)
        return cstruct
