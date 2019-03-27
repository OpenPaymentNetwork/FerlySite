from colander import Email
from colander import Schema
from colander import SchemaNode
from backend.api_schemas import StrippedString


class ContactSchema(Schema):
    email = SchemaNode(StrippedString(), validator=Email())
