from colander import Email
from colander import Decimal
from colander import Invalid
from colander import null
from colander import Range
from colander import SchemaNode
from colander import SchemaType
from colander import String
import cgi
import datetime
import decimal
import phonenumbers
import re

phone_detect_re = re.compile(r'^[(+\s]*[0-9]')

_email_validator = Email()


def amount(minimum=0.01, name='amount'):
    return SchemaNode(
        Decimal(quant='0.01', rounding=decimal.ROUND_HALF_UP),
        name=name,
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


class Recipient(StrippedString):

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
                raise Invalid(node, msg='Invalid phone number')
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


datetime_re = re.compile(
    r'(\d{4})-(\d\d)-(\d\d)'             # date
    r'[T ](\d\d):(\d\d):(\d\d)(\.\d+)?'  # time
    r'(Z|[\+\-]\d\d:?\d\d)?$')           # time zone


def to_datetime(input_str, allow_none=False):
    """Convert a datetime.isoformat() string back to a datetime.

    Accepts a time zone, but converts the datetime to UTC.  (Python's
    support for time zone awareness would add unnecessary complexity to
    most code that uses this function.)
    """
    if allow_none and input_str is None:
        return None
    mo = datetime_re.match(input_str)
    if mo is None:
        raise ValueError("Not a valid datetime: %s" % repr(input_str))
    y, m, d, H, M, S, SS, tz = mo.groups()
    if SS:
        if len(SS) < 7:
            # Pad to microseconds.
            SS = (SS + '000000')[:7]
        ms = int(SS[1:7])
    else:
        ms = 0
    res = datetime.datetime(int(y), int(m), int(d), int(H), int(M), int(S), ms)
    if tz and tz not in ('Z', '+00:00', '-00:00'):
        # Convert to UTC.
        hours = int(tz[:3])
        minutes = int(tz[4:])
        sign = -1 if hours < 0 else 1
        offset = hours * 3600 + sign * minutes * 60
        res -= datetime.timedelta(seconds=offset)
    return res
