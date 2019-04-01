from colander import OneOf
from colander import Schema
from colander import SchemaNode
from colander import String
from backend.appapi.schemas.app_schemas import device_id
from backend.appapi.schemas.app_schemas import recipient


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
