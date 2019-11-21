from backend.appapi.schemas import app_views_schemas
from backend.database.models import Design
from backend.database.models import Customer
from backend.database.serialize import serialize_design
from backend.appapi.utils import notify_customer
from backend.wccontact import wc_contact
from pyramid.view import view_config
from sqlalchemy import cast
import json
from sqlalchemy import func
from sqlalchemy import Unicode
import logging

_last_transfer_notified = ''
log = logging.getLogger(__name__)

@view_config(name='redemption-notification', renderer='json')
def redemption_notification(request):
    """WingCash webhook endpoint for when a customer's card is used."""
    # XXX Security issue: Anyone can trigger this and create havoc.
    # The webhook message should be signed.
    # See: https://github.com/pyauth/requests-http-signature
    if getattr(request, 'content_type', None) == 'application/json':
        param_map = request.json_body
    else:
        param_map = request.params
    source_url = param_map.get('source_url', '')
    transfers = param_map.get('transfers', '')
    ferly_id = request.ferlysettings.wingcash_profile_id
    expect_source = '/p/{0}/webhook'.format(ferly_id)
    if expect_source not in source_url:
        log.warning(
            "Ignoring webhook notification from source %s "
            "because the source does not contain %s",
            repr(source_url), repr(expect_source))
        return {}
    transfers = param_map.get('transfers', [])
    for transfer in transfers:
        transaction_type = transfer.get('appdata.ferly.transactionType','')
        try:
            amount = transfer['amount']
            completed = transfer['completed']
            loop_id = transfer['movements'][0]['loops'][0]['loop_id']
            sender_id = transfer['sender_id']
            transfer_id = transfer['id']
        except Exception:
            log.exception("Error in redemption_notification()")
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
        if transaction_type == 'gift':
            body = 'You gifted ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Gift', body,
                    channel_id='card-used')
        elif transaction_type == 'purchase':
            body = 'Your purchased ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Purchase', body,
                    channel_id='card-used')
        else:
            body = 'Your Ferly card was used to redeem ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Redemption', body,
                    channel_id='card-used')
    return {}


@view_config(name='recaptcha-sitekey', renderer='json')
def recaptcha_sitekey(request):
    response = wc_contact(
        request, 'GET', 'aa/recaptcha_invisible_sitekey', anon=True)
    return response.json()


@view_config(name='list-designs', renderer='json')
def list_designs(request):
    """List all the listable designs on Ferly."""
    dbsession = request.dbsession
    designs = dbsession.query(Design).filter(Design.listable).order_by(
        Design.title).all()
    return [serialize_design(request, design) for design in designs]


@view_config(name='locations', renderer='json')
def locations(request):
    """List location information for redeemers of the cash design."""
    params = request.get_params(app_views_schemas.LocationsSchema())
    design = request.dbsession.query(Design).get(params['design_id'])
    if design is None:
        return {'error': 'invalid_design'}
    response = wc_contact(
        request, 'GET',
        '/design/{0}/redeemers'.format(design.wc_id),
        anon=True)

    locations = []
    for location in response.json():
        locations.append({
            'title': location['title'],
            'address': location['address'],
            'latitude': location['latitude'],
            'longitude': location['longitude']
        })
    return {'locations': locations}


@view_config(name='search-market', renderer='json')
def search_market(request):
    """Search all listable designs."""
    params = request.get_params(app_views_schemas.SearchMarketSchema())
    dbsession = request.dbsession

    # Create an expression that converts the query
    # to a prefix match filter on the design table.
    text_parsed = func.regexp_replace(
        cast(func.plainto_tsquery(params['query']), Unicode),
        r"'( |$)", r"':*\1", 'g')

    designs = dbsession.query(Design).filter(
        Design.listable,
        Design.tsvector.match(text_parsed)
    ).order_by(Design.title)

    return {'results': [serialize_design(request, x) for x in designs]}
