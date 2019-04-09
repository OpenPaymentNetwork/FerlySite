from backend.appapi.schemas import invitation_views_schemas as schemas
from backend.communications import send_email
from backend.communications import send_sms
from backend.database.models import Invitation
from backend.database.serialize import serialize_invitation
from backend.appapi.utils import get_device
from pyramid.view import view_config


@view_config(name='delete-invitation', renderer='json')
def delete_invitation(request):
    params = request.get_params(schemas.DeleteInvitationSchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    invite = dbsession.query(Invitation).get(params['invite_id'])
    if invite is None or invite.customer_id != customer.id:
        return {'error': 'cannot_be_deleted'}
    else:
        invite.status = 'deleted'
    return {}


@view_config(name='existing-invitations', renderer='json')
def existing_invitations(request):
    params = request.get_params(schemas.ExistingInvitationsSchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    status = params.get('status')
    query = dbsession.query(Invitation).filter(
        Invitation.customer_id == customer.id)
    if status:
        query = query.filter(Invitation.status == status)
    return {'results': [serialize_invitation(request, i) for i in query.all()]}


@view_config(name='invite', renderer='json')
def invite(request):
    params = request.get_params(schemas.InviteSchema())
    device = get_device(request, params)
    customer = device.customer
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
        customer_id=customer.id,
        recipient=recipient,
        response=status
    )
    dbsession.add(invitation)
    return {}
