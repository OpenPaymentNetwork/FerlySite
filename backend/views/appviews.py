from backend import schema
from backend.models.models import Contact
from backend.models.models import Design
from backend.models.models import User
from backend.serialize import serialize_design
from backend.serialize import serialize_user
from backend.utils import get_params
from pyramid.view import view_config
from backend.utils import get_device


@view_config(name='recaptcha-sitekey', renderer='json')
def recaptcha_sitekey(request):



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
    users = dbsession.query(User).filter(User.id != user.id).filter(
        ~User.id.in_([10, 11, 71, 51, 89])).all()
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
