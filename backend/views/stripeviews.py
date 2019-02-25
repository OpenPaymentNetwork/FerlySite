from backend.models.models import Design
from backend.wccontact import wc_contact
from backend import schema
from backend.utils import get_device
from backend.utils import get_params
from pyramid.view import view_config
import stripe


@view_config(name='purchase', renderer='json')
def purchase(request):
    param_map = get_params(request)
    params = schema.PurchaseSchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user

    dbsession = request.dbsession
    design = dbsession.query(Design).get(params['design_id'])
    if design is None:
        return {'error': 'invalid_design'}

    amount = params['amount']
    amount_in_cents = int(amount * 100)
    token = params['stripe_token']

    try:
        charge = stripe.Charge.create(
          amount=amount_in_cents,  # must be in cents ie $1 -> 100
          currency='USD',
          capture=False,
          source=token,
          api_key=request.ferlysettings.stripe_api_key,
          statement_descriptor='Ferly Card App'  # 22 character max
        )
    except stripe.error:
        return {'result': False}
    if not charge.paid:
        return {'result': False}

    post_params = {
        'distribution_plan_id': design.distribution_id,
        'recipient_uid': 'wingcash:' + user.wc_id,
        'amount': amount
    }
    wc_contact(request, 'POST', 'design/{0}/send'.format(design.wc_id),
               params=post_params)
    captured_charge = charge.capture()
    return {'result': captured_charge.paid}
