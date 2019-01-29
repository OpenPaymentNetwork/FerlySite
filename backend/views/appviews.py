from backend import schema
from backend.models.models import Contact
from backend.models.models import Design
from backend.models.models import User
from backend.serialize import serialize_design
from backend.serialize import serialize_user
from backend.utils import get_device
from backend.utils import get_params
from backend.wccontact import wc_contact
from pyramid.view import view_config
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import Unicode


@view_config(name='recaptcha-sitekey', renderer='json')
def recaptcha_sitekey(request):
    response = wc_contact(request, 'GET', 'aa/recaptcha_invisible_sitekey')
    return response.json()


@view_config(name='users', renderer='json')
def list_users(request):
    """Return a list of all Ferly users.

    Replace this with a /recipient-search view.
    """
    param_map = get_params(request)
    params = schema.DeviceSchema().bind(request=request).deserialize(param_map)
    device = get_device(request, params=params)
    user = device.user
    dbsession = request.dbsession
    ignored_users = [
        'cf345e5a',  # expo android
        'c4f25505',  # expo ios
        '9005095d',  # test flight
        '91095509',  # test account/surilan
        '9356530a'  # test account/recovery
    ]
    users = dbsession.query(User).filter(User.id != user.id).filter(
        ~User.id.in_(ignored_users)).all()
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
    designs = dbsession.query(Design).all()
    return [serialize_design(request, design) for design in designs]


@view_config(name='search-market', renderer='json')
def search_market(request):
    """Search the list of designs"""
    param_map = get_params(request)
    params = schema.SearchSchema().bind(request=request).deserialize(param_map)
    dbsession = request.dbsession

    # Create an expression that converts the query
    # to a prefix match filter on the design table.
    text_parsed = func.regexp_replace(
        cast(func.plainto_tsquery(params['query']), Unicode),
        r"'( |$)", r"':*\1", 'g')

    designs = dbsession.query(Design).filter(
        Design.tsvector.match(text_parsed))

    return {'results': [serialize_design(request, x) for x in designs]}
