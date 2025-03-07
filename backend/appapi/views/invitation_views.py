from backend.appapi.schemas import invitation_views_schemas as schemas
from backend.communications import send_invite_email
from backend.communications import send_sms
from backend.database.models import Invitation
from backend.database.serialize import serialize_invitation
from backend.appapi.utils import get_device
from backend.appapi.utils import get_wc_token
from backend.wccontact import wc_contact
from datetime import datetime
from pyramid.view import view_config
from sqlalchemy import func


@view_config(name='delete-invitation', renderer='json')
def delete_invitation(request):
    """deletes an invitation"""
    params = request.get_params(schemas.DeleteInvitationSchema())
    device = get_device(request)
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
    """Gets existing invitations"""
    params = request.get_params(schemas.ExistingInvitationsSchema())
    device = get_device(request)
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
    """send out an invitations to join ferly"""
    params = request.get_params(schemas.InviteSchema())
    device = get_device(request)
    customer = device.customer
    dbsession = request.dbsession

    recipient = params['recipient']
    message = 'You have been invited to join Ferly. Download the app and get started! https://appurl.io/iO7GkimtW'
    if '@' in recipient:
        response = send_invite_email(
            request,
            recipient,
            'Ferly Invitation',
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

@view_config(name='accept-code', renderer='json')
def acceptCode(request):
    """Redeems a code to accept invitation cash"""
    params = request.get_params(schemas.AcceptCodeSchema())
    device = get_device(request)
    customer = device.customer
    access_token = get_wc_token(request, customer)
    postParams = {
        'code': params['code']
    }
    response = wc_contact(
        request, 'POST', 'wallet/accept-code', params=postParams,
        access_token=access_token).json()
    if response.get('error'):
        return { 'error': response.get('error')}
    elif response.get('invalid'):
        return { 'invalid': response.get('invalid')}
    else:
        return response

@view_config(name='get-invalid-code-count', renderer='json')
def getInvalidCodeCount(request):
    """Gets the amount of wrong codes given for that day for a customer"""
    device = get_device(request)
    customer = device.customer
    if customer.invalid_date.date() < datetime.now().date():
        customer.invalid_count = '0'
        customer.invalid_date = func.timezone('UTC', func.current_timestamp())
    return { 'count': customer.invalid_count}

@view_config(name='update-invalid-code-count', renderer='json')
def updateInvalidCodeCount(request):
    """Updates the amount of wrong codes given for a day for a customer"""
    params = request.get_params(schemas.updateInvalidCodeCountSchema())
    invalid_result = params.get('invalid_result')
    device = get_device(request)
    customer = device.customer
    if invalid_result:
        if customer.invalid_count == '' or customer.invalid_date.date() < datetime.now().date():
            customer.invalid_count = '1'
            customer.invalid_date = func.timezone('UTC', func.current_timestamp())
        else:
            customer.invalid_count = str(int(customer.invalid_count) + 1)
    else:
        customer.invalid_count = '0'
    return {}

@view_config(name='retract', renderer='json')
def retract(request):
    """retracts a cash invitations"""
    params = request.get_params(schemas.RetractSchema())
    device = get_device(request)
    customer = device.customer
    access_token = get_wc_token(request, customer)
    postParams = {
        'reason': 'other'
    }
    response = wc_contact(
        request, 'POST', 't/' + params['transfer_id'] + '/retract', params=postParams,
        access_token=access_token).json()
    if response.get('error'):
        return { 'error': response.get('error')}
    elif response.get('invalid'):
        return { 'invalid': response.get('invalid')}
    else:
        return response


@view_config(name='change-code-expiration', renderer='json')
def changeCodeExpiration(request):
    """Changes the code expiration on a transfer"""
    params = request.get_params(schemas.changeCodeExpirationSchema())
    device = get_device(request)
    customer = device.customer
    access_token = get_wc_token(request, customer)
    postParams = {
        'paycode': params['code'],
        'expire_seconds': params['seconds']
    }
    response = wc_contact(
        request, 'POST', 't/' + params['transfer_id'] + '/change_paycode_expiration', params=postParams,
        access_token=access_token).json()
    if response.get('error'):
        return { 'error': response.get('error')}
    elif response.get('invalid'):
        return { 'invalid': response.get('invalid')}
    else:
        return response

@view_config(name='resend', renderer='json')
def resend(request):
    """resends a cash invitation"""
    params = request.get_params(schemas.RetractSchema())
    device = get_device(request)
    customer = device.customer
    access_token = get_wc_token(request, customer)
    return wc_contact(
        request, 'POST', 't/' + params['transfer_id'] + '/resend',
        access_token=access_token).json()

@view_config(name='get_transfer_details', renderer='json')
def getTransferDetails(request):
    """gets details about a transfer from wingcash"""
    params = request.get_params(schemas.RetractSchema())
    device = get_device(request)
    customer = device.customer
    access_token = get_wc_token(request, customer)
    return wc_contact(
        request, 'GET', 't/' + params['transfer_id'],
        access_token=access_token).json()
        
