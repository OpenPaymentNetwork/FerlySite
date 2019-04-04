from backend.appapi.schemas import stripe_views_schemas as schemas
from backend.database.models import Design
from backend.appapi.utils import get_device
from backend.wccontact import wc_contact
from colander import Invalid
from pyramid.view import view_config
import stripe
from stripe.error import InvalidRequestError
from stripe.error import CardError


def get_customer(request, stripe_id):
    if not stripe_id:
        return None
    try:
        customer = stripe.Customer.retrieve(
            stripe_id,
            api_key=request.ferlysettings.stripe_api_key
        )
    except InvalidRequestError:
        return None
    else:
        return customer


@view_config(name='list-stripe-sources', renderer='json')
def list_stripe_sources(request):
    params = request.get_params(schemas.CustomerDeviceSchema())
    device = get_device(request, params)
    user = device.user

    customer = get_customer(request, user.stripe_id)
    sources = [] if not customer else customer.sources.data
    return {'sources': [
        {'id': s.id, 'last_four': s.last4, 'brand': s.brand} for s in sources]}


@view_config(name='delete-stripe-source', renderer='json')
def delete_stripe_source(request):
    params = request.get_params(schemas.DeleteSourceSchema())
    device = get_device(request, params)
    user = device.user

    customer = get_customer(request, user.stripe_id)
    if not customer:
        return {'error': 'nonexistent_customer'}

    stripe_response = customer.sources.retrieve(params['source_id']).delete()

    return {'result': stripe_response.get('deleted', False)}


@view_config(name='purchase', renderer='json')
def purchase(request):
    params = request.get_params(schemas.PurchaseSchema())
    device = get_device(request, params)
    user = device.user

    design = request.dbsession.query(Design).get(params['design_id'])
    if design is None:
        return {'error': 'invalid_design'}

    amount = params['amount']
    amount_in_cents = int(amount * 100)
    source_id = params['source_id']

    customer = get_customer(request, user.stripe_id)
    if not customer:
        customer = stripe.Customer.create(
          api_key=request.ferlysettings.stripe_api_key
        )
        user.stripe_id = customer.id

    if source_id.startswith('tok_'):
        try:
            card = customer.sources.create(source=source_id)
        except CardError:
            return {'result': False}
        else:
            card_id = card.id
    elif source_id.startswith('card_'):
        card_id = source_id
    else:
        raise Invalid(None, msg={'source_id': "Invalid payment method"})

    try:
        charge = stripe.Charge.create(
          amount=amount_in_cents,  # must be in cents as int, ie $1.0 -> 100
          currency='USD',
          capture=False,
          customer=customer.id,
          source=card_id,
          api_key=request.ferlysettings.stripe_api_key,
          statement_descriptor='Ferly Card App'  # 22 character max
        )
    except CardError:
        return {'result': False}
    if not charge.paid:
        return {'result': False}

    post_params = {
        'distribution_plan_id': design.distribution_id,
        'recipient_uid': 'wingcash:' + user.wc_id,
        'amount': amount
    }
    wc_response = wc_contact(request, 'POST',
                             'design/{0}/send'.format(design.wc_id),
                             params=post_params)
    if wc_response.status_code != 200:
        return {'result': False}
    captured_charge = charge.capture()
    return {'result': captured_charge.paid}
