from colander import Invalid
from colander import Length
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import StrippedString


def validate_pan(node, value):
    if not value.isdigit():
        raise Invalid(node, "Must contain only numbers")
    if len(value) != 16:
        raise Invalid(node, "Must be exactly 16 digits")

    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(value)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    if checksum % 10:
        raise Invalid(node, "Invalid card number")


def validate_pin(node, value):
    if not value.isdigit():
        raise Invalid(node, "Must contain only numbers")
    if len(value) != 4:
        raise Invalid(node, "Must be exactly 4 digits")


def pin():
    return SchemaNode(StrippedString(), name='pin', validator=validate_pin)


class AddCardSchema(Schema):
    pan = SchemaNode(StrippedString(), validator=validate_pan)
    pin = pin()


class ChangePinSchema(Schema):
    card_id = SchemaNode(String(), validator=Length(max=200))
    pin = pin()


class CardSchema(Schema):
    card_id = SchemaNode(String(), validator=Length(max=200))
