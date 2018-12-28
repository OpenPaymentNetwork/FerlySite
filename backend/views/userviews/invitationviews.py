from backend import schema
from backend.communications import send_email
from backend.communications import send_sms
from backend.models.models import Invitation
from backend.serialize import serialize_invitation
from backend.utils import get_device
from backend.utils import get_params
from pyramid.view import view_config


@view_config(name='delete-invitation', renderer='json')
def delete_invitation(request):
    param_map = get_params(request)
    params = schema.DeleteInvitationSchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    invite = dbsession.query(Invitation).get(params['invite_id'])
    if invite is None or invite.user_id != user.id:
        return {'error': 'cannot_be_deleted'}
    else:
        invite.status = 'deleted'
    return {}


@view_config(name='existing-invitations', renderer='json')
def existing_invitations(request):
    param_map = get_params(request)
    params = schema.ExistingInvitationsSchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    status = params.get('status')
    query = dbsession.query(Invitation).filter(Invitation.user_id == user.id)
    if status:
        query = query.filter(Invitation.status == status)
    return {'results': [serialize_invitation(request, i) for i in query.all()]}


@view_config(name='invite', renderer='json')
def invite(request):
    param_map = get_params(request)
    params = schema.InviteSchema().bind(request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    recipient = params['recipient']
    message = 'You have been invited to join Ferly.'
    if '@' in recipient:
        response = send_email(
            request,
            recipient,
            'Ferly Invitation',
            message
        )
        status = 'sendgrid:{0}'.format(response)
    else:
        response = send_sms(request, recipient, message)
        status = 'twilio:{0}'.format(response)

    invitation = Invitation(
        user_id=user.id,
        recipient=recipient,
        response=status
    )
    dbsession.add(invitation)
    return {}
