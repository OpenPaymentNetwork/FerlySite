from backend.appapi.schemas import app_schemas
from backend.database.models import Design
from backend.database.models import Customer
from backend.database.serialize import serialize_design
from backend.appapi.utils import notify_customer
from backend.wccontact import wc_contact
from pyramid.view import view_config
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import Unicode

_last_transfer_notified = ''


@view_config(name='redemption-notification', renderer='json')
def redemption_notification(request):
    """WingCash webhook endpoint for when a customer's card is used."""
    if getattr(request, 'content_type', None) == 'application/json':
        param_map = request.json_body
    else:
        param_map = request.params
    source_url = param_map.get('source_url', '')
    ferly_id = request.ferlysettings.wingcash_profile_id
    if '/p/{0}/webhook'.format(ferly_id) not in source_url:
        return {}
    transfers = param_map.get('transfers', [])
    for transfer in transfers:
        try:
            amount = transfer['amount']
            completed = transfer['completed']
            loop_id = transfer['movements'][0]['loops'][0]['loop_id']
            sender_id = transfer['sender_id']
            transfer_id = transfer['id']
        except Exception:
            continue
        if not completed:
            continue
        global _last_transfer_notified
        if _last_transfer_notified == transfer_id:
            continue
        _last_transfer_notified = transfer_id
        dbsession = request.dbsession
        customer = dbsession.query(
            Customer).filter(Customer.wc_id == sender_id).first()
        design = dbsession.query(Design).filter(
            Design.wc_id == loop_id).first()
        if not customer or not design:
            continue
        body = 'Your Ferly card was used to redeem ${0} {1}.'.format(
            amount, design.title)
        notify_customer(request, customer, 'Redemption', body,
                        channel_id='card-used')
    return {}


@view_config(name='recaptcha-sitekey', renderer='json')
def recaptcha_sitekey(request):
    response = wc_contact(request, 'GET', 'aa/recaptcha_invisible_sitekey')
    return response.json()


@view_config(name='list-designs', renderer='json')
def list_designs(request):
    """List all the designs on Ferly."""
    dbsession = request.dbsession
    designs = dbsession.query(Design).order_by(Design.title).all()
    return [serialize_design(request, design) for design in designs]


@view_config(name='search-market', renderer='json')
def search_market(request):
    """Search the list of designs"""
    params = request.get_params(app_schemas.SearchMarketSchema())
    dbsession = request.dbsession

    # Create an expression that converts the query
    # to a prefix match filter on the design table.
    text_parsed = func.regexp_replace(
        cast(func.plainto_tsquery(params['query']), Unicode),
        r"'( |$)", r"':*\1", 'g')

    designs = dbsession.query(Design).filter(
        Design.tsvector.match(text_parsed)).order_by(Design.title)

    return {'results': [serialize_design(request, x) for x in designs]}
