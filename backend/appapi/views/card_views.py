from backend.appapi.schemas import card_views_schemas as schemas
from backend.appapi.utils import get_device
from backend.appapi.utils import get_wc_token
from backend.wccontact import wc_contact
from pyramid.view import view_config


@view_config(name='add-card', renderer='json')
def add_card(request):
    """Associate a card with the customer."""
    params = request.get_params(schemas.AddCardSchema())
    device = get_device(request, params)
    customer = device.customer
    access_token = get_wc_token(request, customer,
                                permissions=['link_paycard'])
    card_params = {'pan': params['pan'], 'pin': params['pin']}
    response = wc_contact(request, 'POST', 'wallet/paycard/link',
                          params=card_params, access_token=access_token)
    return {'result': response.json()['linked']}


@view_config(name='delete-card', renderer='json')
def delete_card(request):
    """Disassociate the card and the customer."""
    params = request.get_params(schemas.CardSchema())
    device = get_device(request, params)
    customer = device.customer
    access_token = get_wc_token(request, customer,
                                permissions=['link_paycard'])
    card_params = {'card_id': params['card_id']}
    wc_contact(request, 'POST', 'wallet/paycard/delete', params=card_params,
               access_token=access_token)
    return {}


@view_config(name='change-pin', renderer='json')
def change_pin(request):
    """Replace the card's pin with a new one."""
    params = request.get_params(schemas.ChangePinSchema())
    device = get_device(request, params)
    customer = device.customer
    access_token = get_wc_token(request, customer,
                                permissions=['link_paycard'])
    pin_params = {'card_id': params['card_id'], 'pin': params['pin']}
    wc_contact(request, 'POST', 'wallet/paycard/set-pin', params=pin_params,
               access_token=access_token)
    return {}


@view_config(name='suspend-card', renderer='json')
def suspend_card(request):
    """Disable the card's ability to spend cash without deleting it."""
    params = request.get_params(schemas.CardSchema())
    device = get_device(request, params)
    customer = device.customer
    access_token = get_wc_token(request, customer,
                                permissions=['link_paycard'])
    card_params = {'card_id': params['card_id']}
    wc_contact(request, 'POST', 'wallet/paycard/suspend', params=card_params,
               access_token=access_token)
    return {}


@view_config(name='unsuspend-card', renderer='json')
def unsuspend_card(request):
    """Reenable the card's ability to spend cash."""
    params = request.get_params(schemas.CardSchema())
    device = get_device(request, params)
    customer = device.customer
    access_token = get_wc_token(request, customer,
                                permissions=['link_paycard'])
    card_params = {'card_id': params['card_id']}
    wc_contact(request, 'POST', 'wallet/paycard/unsuspend', params=card_params,
               access_token=access_token)
    return {}
