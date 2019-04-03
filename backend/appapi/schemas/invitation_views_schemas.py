from colander import OneOf
from colander import SchemaNode
from colander import String
from backend.api_schemas import Recipient
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema


class DeleteInvitationSchema(CustomerDeviceSchema):
    invite_id = SchemaNode(String())


class ExistingInvitationsSchema(CustomerDeviceSchema):
    status = SchemaNode(
        String(),
        missing=None,
        validator=OneOf(['pending', 'deleted', 'accepted']))


class InviteSchema(CustomerDeviceSchema):
    recipient = SchemaNode(Recipient())
