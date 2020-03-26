
from backend.appapi.schemas import stripe_views_schemas as schemas
from backend.database.models import Design
from backend.appapi.utils import get_device
from backend.wccontact import wc_contact
from colander import Invalid
from pyramid.view import view_config
import logging
import stripe
from stripe.error import InvalidRequestError
from stripe.error import CardError

log = logging.getLogger(__name__)


def get_stripe_customer(request, stripe_id):
    if not stripe_id:
        return None
    try:
        customer = stripe.Customer.retrieve(
            stripe_id,
            api_key=request.ferlysettings.stripe_api_key
        )
    except InvalidRequestError:
        log.warning(
            "InvalidRequestError while retrieving Stripe customer "
            "with stripe_id = %s", stripe_id)
        return None
    else:
        return customer


@view_config(name='list-stripe-sources', renderer='json')
def list_stripe_sources(request):
    device = get_device(request)
    customer = device.customer

    stripe_customer = get_stripe_customer(request, customer.stripe_id)
    sources = [] if not stripe_customer else stripe_customer.sources.data
    return {'sources': [
        {'id': s.id, 'last_four': s.last4, 'brand': s.brand} for s in sources]}


@view_config(name='delete-stripe-source', renderer='json')
def delete_stripe_source(request):
    params = request.get_params(schemas.DeleteSourceSchema())
    device = get_device(request)
    customer = device.customer

    stripe_customer = get_stripe_customer(request, customer.stripe_id)
    if not stripe_customer:
        log.warning(
            "delete_stripe_source() returning 'nonexistent_customer' "
            "with stripe_id=%s", customer.stripe_id)
        return {'error': 'nonexistent_customer'}

    stripe_response = stripe_customer.sources.retrieve(
        params['source_id']).delete()

    return {'result': stripe_response.get('deleted', False)}


def get_distributor_token(request, permissions=['apply_design'], open_loop=False):
    """Get an access token for distributing cash to the purchaser."""
    ferlysettings = request.ferlysettings
    params = {
        'uid': ferlysettings.distributor_uid,
        'manager_uid': ferlysettings.distributor_manager_uid,
        'concurrent': True,
        'permissions': permissions,
    }
    response = wc_contact(request, 'POST', 'p/token', params, auth=True, open_loop=open_loop)
    try:
        response.raise_for_status()
    except Exception:
        log.exception(
            "Error while getting distributor token from OPN: %s",
            repr(response.text))
        # Propagate the error.
        raise
    return response.json().get('access_token')

@view_config(name='purchase', renderer='json')
def purchase(request):
    params = request.get_params(schemas.PurchaseSchema())
    device = get_device(request)
    customer = device.customer
    design = request.dbsession.query(Design).get(params['design_id'])
    if design is None:
        log.warning(
            "purchase() returning 'invalid_design' with design_id=%s",
            params['design_id'])
        return {'error': 'invalid_design'}
    amount = params['amount']
    amount_in_cents = int(amount * 100)
    fee = params['fee']
    fee_amount_in_cents = int(fee * 100)
    source_id = params['source_id']

    if fee != design.fee:
        log.warning(
            "purchase() returning 'fee_mismatch' with "
            "design.fee = %s, specified fee = %s",
            design.fee, fee)
        return {'error': 'fee_mismatch'}

    distributor_token = get_distributor_token(request)

    stripe_customer = get_stripe_customer(request, customer.stripe_id)
    if not stripe_customer:
        stripe_customer = stripe.Customer.create(
          api_key=request.ferlysettings.stripe_api_key
        )
        customer.stripe_id = stripe_customer.id

    if source_id.startswith('tok_'):
        try:
            card = stripe_customer.sources.create(source=source_id)
        except CardError:
            log.exception(
                "purchase() returning result = false due to CardError "
                "on sources.create(). stripe_customer.id = %s, source_id = %s",
                stripe_customer.id, source_id)
            return {'result': False}
        else:
            card_id = card.id
    elif source_id.startswith('card_'):
        card_id = source_id
    else:
        raise Invalid(None, msg={'source_id': "Invalid payment method"})

    charge_amount_in_cents = amount_in_cents + fee_amount_in_cents
    try:
        charge = stripe.Charge.create(
          amount=charge_amount_in_cents,  # must be in cents, ie $1.0 -> 100
          currency='USD',
          capture=False,
          customer=stripe_customer.id,
          source=card_id,
          api_key=request.ferlysettings.stripe_api_key,
          statement_descriptor='Ferly Card App'  # 22 character max
        )
    except CardError:
        log.exception(
            "purchase() returning result = false due to CardError "
            "on Charge.create(). stripe_customer.id = %s, card_id = %s",
            stripe_customer.id, card_id)
        return {'result': False}
    if not charge.paid:
        log.warning(
            "purchase() returning result = false because charge.paid "
            "is not true. stripe_customer.id = %s, card_id = %s",
            stripe_customer.id, card_id)
        return {'result': False}

    post_params = {
        'distribution_plan_id': design.distribution_id,
        'recipient_uid': 'wingcash:' + customer.wc_id,
        'amount': str(amount),
        'appdata.ferly.convenience_fee': str(fee),
        'appdata.ferly.stripe_brand': charge.payment_method_details.card.brand,
        'appdata.ferly.stripe_last4': charge.payment_method_details.card.last4,
        'appdata.ferly.transactionType': 'purchase',
    }
    wc_response = wc_contact(
        request, 'POST',
        'design/{0}/send'.format(design.wc_id),
        params=post_params,
        access_token=distributor_token)
    if wc_response.status_code != 200:
        log.warning(
            "purchase() returning result = false because "
            "wc_response.status_code = %s. "
            "stripe_customer.id = %s, card_id = %s, post_params = %s",
            wc_response.status_code, stripe_customer.id, card_id, post_params)
        return {'result': False}

    captured_charge = charge.capture()
    if not captured_charge.paid:
        log.warning(
            "purchase() returning result = false because "
            "captured_charge.paid is false. "
            "stripe_customer.id = %s, card_id = %s",
            stripe_customer.id, card_id)
    return {'result': captured_charge.paid}
