from backend.merchantapi.schemas import site_schemas
from backend.database.models import Contact
from pyramid.view import view_config


@view_config(name='create-contact', renderer='json')
def create_contact(request):
    """Store an email address of someone who wants to
    receive company updates.
    """
    params = request.get_params(site_schemas.ContactSchema())
    dbsession = request.dbsession
    email = params['email']
    contact = Contact(email=email)
    dbsession.add(contact)
    return {}
