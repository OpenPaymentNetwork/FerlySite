from backend.appapi.schemas import customer_views_schemas as schemas
from backend.database.models import Design
from backend.database.models import Device
from backend.database.models import Customer
from backend.database.serialize import serialize_customer
from backend.appapi.utils import get_device
from backend.appapi.utils import notify_customer
from backend.appapi.utils import get_wc_token
from backend.wccontact import wc_contact
from pyramid.view import view_config
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import Unicode
import boto3
import os
import uuid


@view_config(name='signup', renderer='json')
def signup(request):
    """Associate a device with a new customer and wallet."""
    params = request.get_params(schemas.RegisterSchema())
    device_id = params['device_id']
    expo_token = params['expo_token']
    os = params['os']
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    if device is not None:
        return {'error': 'device_already_registered'}
    else:
        username = params['username']
        existing_customer = dbsession.query(Customer).filter(
            Customer.username == username).first()

        if existing_customer is not None:
            return {'error': 'existing_username'}

        postParams = {
            'first_name': params['first_name'],
            'last_name': params['last_name'],
            'agreed_terms_and_privacy': True
        }

        response = wc_contact(
            request,
            'POST',
            'p/add-individual',
            params=postParams,
            auth=True)

        wc_id = response.json().get('id')
        first_name = params['first_name']
        last_name = params['last_name']
        new_customer = Customer(wc_id=wc_id, first_name=first_name,
                                last_name=last_name, username=username)
        new_customer.update_tsvector()
        dbsession.add(new_customer)
        dbsession.flush()

        device = Device(device_id=device_id, customer_id=new_customer.id,
                        expo_token=expo_token, os=os)
        dbsession.add(device)
    return {}


@view_config(name='is-customer', renderer='json')
def is_customer(request):
    """Return if the device_id is associated with a customer."""
    params = request.get_params(schemas.IsCustomerSchema())
    if params['expected_env'] != request.ferlysettings.environment:
        return {'error': 'unexpected_environment'}
    device_id = params['device_id']
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    # Doing more than this requires updating device.last_used to models.now_utc
    return {'is_customer': device is not None}


@view_config(name='profile', renderer='json')
def profile(request):
    """Describe the profile currently associated with a device."""
    params = request.get_params(schemas.CustomerDeviceSchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    access_token = get_wc_token(request, customer,
                                permissions=['view_paycard', 'view_wallet'])
    response = wc_contact(request, 'GET', 'wallet/info',
                          access_token=access_token)
    card_response = wc_contact(request, 'GET', 'wallet/paycard/list',
                               access_token=access_token)

    profile = response.json()['profile']
    uids = [uid_info['uid'] for uid_info in profile['confirmed_uids']]
    amounts = []
    loops = profile.get('holdings', [])
    for loop in loops:
        # use memcached here
        design = dbsession.query(Design).filter(
            Design.wc_id == loop['loop_id']).first()
        if design:
            amounts.append({
                'id': design.id,
                'title': loop['title'],
                'amount': loop['amount'],
                'wallet_image_url': design.wallet_image_url,
                'logo_image_url': design.logo_image_url})

    recents = [dbsession.query(
        Customer).get(recent) for recent in customer.recents]

    return {
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'username': customer.username,
        'profile_image_url': customer.profile_image_url,
        'amounts': amounts,
        'uids': uids,
        'recents': [serialize_customer(request, r) for r in recents],
        'cards': card_response.json()['cards']
    }


@view_config(name='send', renderer='json')
def send(request):
    """Send Closed Loop Cash to another Ferly customer."""
    params = request.get_params(schemas.SendSchema())
    device = get_device(request, params)
    customer = device.customer

    recipient_id = params['recipient_id']
    design_id = params['design_id']
    amount = params['amount']
    message = params['message']

    dbsession = request.dbsession
    recipient = dbsession.query(Customer).get(recipient_id)
    design = dbsession.query(Design).get(design_id)
    amount_row = "{0}-USD-{1}".format(design.wc_id, amount)

    params = {
        'sender_id': customer.wc_id,
        'recipient_uid': 'wingcash:{0}'.format(recipient.wc_id),
        'amounts': amount_row,
        'require_recipient_email': False,
        'accepted_policy': True
    }

    if message:
        params['message'] = message

    customer.recents.add(recipient.id)

    access_token = get_wc_token(request, customer)
    wc_contact(request, 'POST', 'wallet/send', params=params,
               access_token=access_token)

    formatted_amount = '${:.2f}'.format(amount)

    title = 'Received {0} {1}'.format(formatted_amount, design.title)
    sender = 'from {0}'.format(customer.title)
    body = '{0}\n{1}'.format(message, sender) if message else sender
    notify_customer(
        request, recipient, title, body, channel_id='gift-received')

    return {}


@view_config(name='edit-profile', renderer='json')
def edit_profile(request):
    """Update a customer's profile information"""
    params = request.get_params(schemas.EditProfileSchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    first_name = params['first_name']
    last_name = params['last_name']
    username = params['username']
    existing_customer = dbsession.query(Customer).filter(
        Customer.username == username).first()

    if existing_customer is not None and existing_customer is not customer:
        return {'error': 'existing_username'}
    if first_name != customer.first_name or last_name != customer.last_name:
        post_params = {
            'first_name': first_name,
            'last_name': last_name
        }
        access_token = get_wc_token(request, customer)
        wc_contact(request, 'POST', 'wallet/change-name',
                   params=post_params, access_token=access_token)
    customer.first_name = first_name
    customer.last_name = last_name
    customer.username = username
    customer.update_tsvector()
    return {}


@view_config(name='history', renderer='json')
def history(request):
    """Request and return the customer's WingCash transfer history."""
    params = request.get_params(schemas.HistorySchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    post_params = {'limit': params['limit'], 'offset': params['offset']}

    access_token = get_wc_token(request, customer)
    response = wc_contact(
        request, 'GET', 'wallet/history', params=post_params,
        access_token=access_token)

    json = response.json()
    results = json.get('results', [])
    has_more = bool(json.get('more'))
    history = []
    designs = {}
    for transfer in results:
        amount = transfer['amount']
        timestamp = transfer['timestamp']
        title = 'Unrecognized'
        logo_image_url = ''
        try:
            # TODO Make sure all loop_ids are the same
            first_movement_loop = transfer['movements'][0]['loops'][0]
            loop_id = first_movement_loop['loop_id']
        except Exception:
            # No money was moved. ie waiting or canceled transfer
            pass
        else:
            # TODO Get CLC title from memcache by loop_id or call wingcash and
            # cache it in parallel
            design = designs.get(loop_id)
            if not design:
                design = dbsession.query(Design).filter(
                    Design.wc_id == loop_id).first()
                designs[loop_id] = design
            if design:
                title = design.title
                logo_image_url = design.logo_image_url

        sender_info = transfer['sender_info']
        recipient_info = transfer['recipient_info']
        transfer_type = 'unrecognized'
        counter_party = ''
        if transfer['recipient_id'] == customer.wc_id:
            counter_party = sender_info['title']
            if not bool(sender_info['is_individual']):
                transfer_type = 'purchase'
            else:
                transfer_type = 'receive'
        elif transfer['sender_id'] == customer.wc_id:
            counter_party = recipient_info['title']
            if bool(recipient_info['is_individual']):
                transfer_type = 'send'
            else:
                transfer_type = 'redeem'

        history.append({
            'id': transfer['id'],
            'amount': amount,
            'transfer_type': transfer_type,
            'counter_party': counter_party,
            'design_title': title,
            'design_logo_image_url': logo_image_url,
            'timestamp': timestamp,
            # 'loop_id': loop_id
        })
    return {'history': history, 'has_more': has_more}


@view_config(name='transfer', renderer='json')
def transfer(request):
    """Request and return WingCash transfer details of a transfer."""
    params = request.get_params(schemas.TransferSchema())
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    access_token = get_wc_token(request, customer)
    transfer = wc_contact(
        request,
        'GET',
        't/{0}'.format(params['transfer_id']),
        access_token=access_token).json()

    sender_info = transfer['sender_info']
    recipient_info = transfer['recipient_info']
    if transfer['recipient_id'] == customer.wc_id:
        counter_party = sender_info
    elif transfer['sender_id'] == customer.wc_id:
        counter_party = recipient_info
    else:
        return {'error': 'permission_denied'}

    profile_image_url = ''
    #  is_individual may not always be accurate, according to WingCash.
    if bool(counter_party['is_individual']):
        cp_customer = dbsession.query(Customer).filter(
            Customer.wc_id == counter_party['uid_value']).first()
        if cp_customer is not None:
            profile_image_url = cp_customer.profile_image_url

    return {
        'message': transfer['message'],
        'counter_party_profile_image_url': profile_image_url
    }


@view_config(name='search-customers', renderer='json')
def search_customers(request):
    """Search the list of customers"""
    params = request.get_params(schemas.SearchCustomersSchema())
    dbsession = request.dbsession
    device = get_device(request, params)
    customer = device.customer
    dbsession = request.dbsession

    # Create an expression that converts the query
    # to a prefix match filter on the design table.
    text_parsed = func.regexp_replace(
        cast(func.plainto_tsquery(params['query']), Unicode),
        r"'( |$)", r"':*\1", 'g')

    customers = dbsession.query(Customer).filter(
        Customer.tsvector.match(text_parsed),
        Customer.id != customer.id).order_by(Customer.username)

    return {'results': [serialize_customer(request, c) for c in customers]}


@view_config(name='upload-profile-image', renderer='json')
def upload_profile_image(request):
    """Allow a customer to upload an image for their profile picture"""
    params = request.get_params(schemas.UploadProfileImageSchema())
    device = get_device(request, params)
    customer = device.customer
    image = params['image']
    content_type = image.type
    file_type = content_type.split('/')[-1]

    access_key_id = request.ferlysettings.aws_access_key_id
    secret_key = request.ferlysettings.aws_secret_key
    new_file_name = '{0}|{1}.{2}'.format(
        customer.id, str(uuid.uuid4()), file_type)
    region = 'us-east-2'
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    s3Url = 'https://s3.{0}.amazonaws.com/'.format(region)
    bucket_name = 'ferly-user-images'
    if request.ferlysettings.environment == 'production':
        bucket_name = 'ferly-prod-user-images'
    s3_resource = session.resource('s3')

    current_image = customer.profile_image_url
    if current_image:
        current_image_split = current_image.split('/')
        current_image_file = current_image_split[-1]
        current_bucket = current_image_split[-2]
        obj = s3_resource.Object(current_bucket, current_image_file)
        obj.delete()

    s3_resource.Bucket(bucket_name).upload_fileobj(
        Fileobj=image.file,
        Key=new_file_name,
        ExtraArgs={'ACL': 'public-read', 'ContentType': content_type})
    customer.profile_image_url = os.path.join(
        s3Url, bucket_name, new_file_name)

    return {}
