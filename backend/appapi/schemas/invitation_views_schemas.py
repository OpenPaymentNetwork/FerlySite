from colander import Length
from colander import OneOf
from colander import Schema
from colander import SchemaNode
from colander import String
from colander import Decimal
from backend.api_schemas import Recipient


class DeleteInvitationSchema(Schema):
    invite_id = SchemaNode(String(), validator=Length(max=100))


class ExistingInvitationsSchema(Schema):
    status = SchemaNode(
        String(),
        missing=None,
        validator=OneOf(['pending', 'deleted', 'accepted']))


class InviteSchema(Schema):
    recipient = SchemaNode(Recipient())
