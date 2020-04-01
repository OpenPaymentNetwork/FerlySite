from backend.appapi.schemas import app_views_schemas
from backend.appapi.views.customer_views import completeTrade
from backend.appapi.views.customer_views import completeAcceptTrade
from backend.database.models import Design
from backend.database.models import Customer
from backend.database.serialize import serialize_design
from backend.appapi.utils import get_device
from backend.appapi.utils import notify_customer
from backend.wccontact import wc_contact
import decimal
from datetime import datetime
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
    log.info("Entered redemption-notification call")
    
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
        dbsession = request.dbsession
        transaction_type = transfer.get('appdata.ferly.transactionType','')
        sender_id = transfer.get('sender_id','')
        recipient_id = transfer.get('recipient_id', '')
        workflow_type = transfer.get('workflow_type', '')
        if workflow_type == 'trade':
            continue
        try:
            amount = transfer['amount']
            completed = transfer['completed']
            loop_id = transfer['movements'][0]['loops'][0]['loop_id']
            currency = transfer['movements'][0]['loops'][0]['currency']
            transfer_id = transfer['id']
        except Exception:
            if transfer.get('reason') != '' and sender_id:
                customer = dbsession.query(
            Customer).filter(Customer.wc_id == sender_id).first()
                if customer:
                    notify_customer(request, customer, 'Oops!', "An attempt to use your Ferly Card was unsuccessful.",
                        channel_id='card-used', data={'type': 'redemption_error', 'reason': transfer.get('reason')})
                else:
                    log.exception("Error in redemption_notification()")
                    continue
            else:
                log.exception("Error in redemption_notification()")
                continue
        if not completed:
            continue
        # if this becomes a problem a fix can be to create a table that remembers when a notification was sent.
        global _last_transfer_notified
        if _last_transfer_notified == transfer_id:
            continue
        _last_transfer_notified = transfer_id
        customer = dbsession.query(
            Customer).filter(Customer.wc_id == sender_id).first()
        design = dbsession.query(Design).filter(
            Design.wc_id == loop_id).first()
        if loop_id != '0' and (not customer or not design):
            continue
        if transaction_type == 'gift':
            body = 'You gifted ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Gift', body,
                    channel_id='card-used')
            log.info("Notified Customer: "+ customer.id+" of gift")
        elif transaction_type == 'purchase':
            body = 'Your purchased ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Purchase', body,
                    channel_id='card-used')
            log.info("Notified Customer: "+ customer.id+" of purchase")
        elif loop_id == '0' and currency == 'USD':
            ferlyCashDesign = dbsession.query(Design).filter(
                Design.title == 'Ferly Cash').first()
            rewardCashDesign = dbsession.query(Design).filter(
                Design.title == 'Ferly Rewards').first()
            if ferlyCashDesign:
                customer = dbsession.query(
                    Customer).filter(Customer.wc_id == recipient_id).first()
                rewards = str(round(decimal.Decimal(amount)*decimal.Decimal(.05),2))
                params = {
                    'amounts': [amount],
                    'loop_ids': ['0'],
                    'expect_amounts': [amount, rewards],
                    'expect_loop_ids': [ferlyCashDesign.id, rewardCashDesign.id],
                    'open_loop': True
                }
                response = completeTrade(request, params, customer)
                transfer = response.get('transfer')
                if transfer:
                    params2 = {
                        'loop_ids': [ferlyCashDesign.id, rewardCashDesign.id],
                        'transfer_id': transfer.get('id'),
                        'open_loop': True
                    }
                    response = completeAcceptTrade(request, params2, customer)
        else:
            body = 'Your Ferly card was used to redeem ${0} {1}.'.format(
                amount, design.title)
            notify_customer(request, customer, 'Redemption', body,
                    channel_id='card-used')
            log.info("Notified Customer: "+ customer.id+" of redemption")
    return {}


@view_config(name='recaptcha-sitekey', renderer='json')
def recaptcha_sitekey(request):
    response = wc_contact(
        request, 'GET', 'aa/recaptcha_invisible_sitekey', anon=True)
    return response.json()


@view_config(name='list-designs', renderer='json')
def list_designs(request):
    """List all the listable designs on Ferly."""
    get_device(request)
    dbsession = request.dbsession
    designs = dbsession.query(Design).filter(Design.listable).order_by(
        Design.title).all()
    return [serialize_design(request, design) for design in designs]

@view_config(name='get-ferly-cash-design', renderer='json')
def get_ferly_cash_design(request):
    """List all the listable designs on Ferly."""
    get_device(request)
    dbsession = request.dbsession
    design = dbsession.query(Design).filter(
        Design.title == 'Ferly Cash').first()
    return serialize_design(request, design)

@view_config(name='list-loyalty-designs', renderer='json')
def list_Loyalty_designs(request):
    """List all the listable designs on Ferly."""
    print("here in list loyalty")
    get_device(request)
    dbsession = request.dbsession
    designs = dbsession.query(Design).filter(
        Design.title.contains('Loyalty')).all()
    print("here in list loyalty2")
    return [serialize_design(request, design) for design in designs]


@view_config(name='locations', renderer='json')
def locations(request):
    """List location information for redeemers of the cash design."""
    params = request.get_params(app_views_schemas.LocationsSchema())
    get_device(request)
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
    get_device(request)
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
