from backend import schema
from backend.models.models import Contact
from backend.models.models import Design
from backend.models.models import User
from backend.serialize import serialize_design
from backend.serialize import serialize_user
from backend.utils import get_params
# from backend.wccontact import wc_contact
from pyramid.view import view_config
from backend.utils import get_device


@view_config(name='users', renderer='json')
def list_users(request):
    """Return a list of all Ferly users.

    Replace this with a search userview that called WingCash search endpoint.
    """
    param_map = get_params(request)
    params = schema.WalletSchema().bind(request=request).deserialize(param_map)
    device = get_device(request, params=params)
    user = device.user
    dbsession = request.dbsession
    users = dbsession.query(User).filter(User.id != user.id).filter(
        ~User.id.in_([10, 11, 12, 71, 51])).all()
    # User.device_id != request.params.get('device_id')).all()
    return [serialize_user(request, u) for u in users]


@view_config(name='create-contact', renderer='json')
def create_contact(request):
    """Store an email address of someone who wants to
    receive company updates.
    """
    param_map = get_params(request)
    params = schema.ContactSchema().bind(
        request=request).deserialize(param_map)
    dbsession = request.dbsession
    email = params['email']
    contact = Contact(email=email)
    dbsession.add(contact)
    return {}


@view_config(name='list-designs', renderer='json')
def list_designs(request):
    """List all the designs on Ferly.

    Replace this with a request to WingCash, to get all designs associataed
    with the Ferly profile.
    """
    dbsession = request.dbsession
    designs = dbsession.query(Design).filter(
        ~Design.title.in_(['Amazon', 'Apple'])).all()
    return [serialize_design(request, design) for design in designs]


# @view_config(name='design', renderer='json')
# def design(request):
#     param_map = get_params(request)
#     params =
# schema.DesignSchema().bind(request=request).deserialize(param_map)

#     dbsession = request.dbsession
#     design = dbsession.query(Design).get(params['design_id'])

#     if not design:
#         return {'error': 'invalid design id'}

#     response = wc_contact(request, 'GET', 'o/list')
#     print('response:', response.json())

#     # Currently only supports free offers with one design
#     offers = []
#     for offer in response.json()['offers']:
#         base_loops = offer['base_loops']
#         loop = base_loops[0]
#         if len(base_loops) > 1 or design.wc_id != loop['loop_id']:
#             continue

#         response_offer = {}
#         response_offer['title'] = offer['title']
#         response_offer['purchase_amount'] = offer['amount']
#         response_offer['image'] = offer['metadata_image']
#         # response_offer['show_amount_as'] = offer['show_amount_as']
#         response_offer['receive_amount'] = loop['amount']
#         response_offer['id'] = offer['id']
#         # no need to expose option id to the app, later use memcached in the
#         # accept call to see if we know it from the offer (because only
#         # one option), otherwise ask wingcash for details on that offer
#         response_offer['option_id'] = offer['options'][0]['id']
#         offers.append(response_offer)

#     # in an offer return:
#     # title
#     # show_limit
#     # show_amount_as
#     # require confirmation ?
#     # render_status
#     # purchases_remain
#     # metadata_image url
#     # id
#     # base_loops
#     # amount

#     return {'offers': offers}
