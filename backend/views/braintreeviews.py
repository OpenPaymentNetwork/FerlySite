from backend.models.models import Design
from backend.wccontact import wc_contact
from backend import schema
from backend.utils import get_device
from backend.utils import get_params
from pyramid.view import view_config
import braintree

# TODO move these keys to dev keys
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="c8ktv79ssh35mdfq",
        public_key="t7zvd8kfhz4bwp7x",
        private_key="ce5719ffc1d674e490706bd32b8caf3e"
    )
)


@view_config(name='request-token', renderer='json')
def request_token(request):
    param_map = get_params(request)
    params = schema.DeviceSchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user

    try:
        customer = gateway.customer.find(str(user.id))
    except (braintree.exceptions.not_found_error.NotFoundError):
        result = gateway.customer.create({
            "id": str(user.id)
        })
        customer = result.customer

    client_token = gateway.client_token.generate({
        "customer_id": customer.id
    })
    return {'token': client_token}


@view_config(name='create-purchase', renderer='json')
def create_purchase(request):
    param_map = get_params(request)
    params = schema.PurchaseSchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user

    dbsession = request.dbsession
    design = dbsession.query(Design).get(params['design_id'])
    amount = params['amount']
    nonce = params['nonce']

    if design is None:
        return {'error': 'invalid_design'}

    result = gateway.transaction.sale({
        "amount": str(amount),
        "payment_method_nonce": nonce,
        "options": {
            "store_in_vault_on_success": True
        }
    })

    if result.is_success:
        post_params = {
            'distribution_plan_id': design.distribution_id,
            'recipient_uid': 'wingcash:' + user.wc_id,
            'amount': amount
        }

        wc_contact(
            request,
            'POST',
            'design/{0}/send'.format(design.wc_id),
            params=post_params)
        settle_response = gateway.transaction.submit_for_settlement(
            result.transaction.id)
        return {'result': settle_response.is_success}

    return {'result': result.is_success}
