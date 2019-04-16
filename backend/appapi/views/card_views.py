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
    access_token = get_wc_token(
        request, customer, permissions=['link_paycard'])
    card_params = {'pan': params['pan'], 'pin': params['pin']}
    response = wc_contact(request, 'POST', 'wallet/paycard/link',
                          params=card_params, access_token=access_token)
    return {'result': response.json()['linked']}
