from backend.appapi.schemas import customer_views_schemas as schemas
from backend.appapi.utils import get_device
from backend.appapi.utils import get_device_token
from backend.appapi.utils import get_wc_token
from backend.appapi.utils import notify_customer
from backend.appapi.utils import recovery_error
from backend.database.models import CardRequest
from backend.database.models import Customer
from backend.database.models import Design
from backend.database.models import Device
from backend.database.serialize import serialize_customer
from backend.database.serialize import serialize_design
from backend.wccontact import wc_contact
from colander import Invalid
from markupsafe import escape
from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.view import view_config
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import Unicode
from xml.etree import ElementTree
import boto3
import hashlib
import logging
import os
import requests
import uuid
import json
log = logging.getLogger(__name__)

@view_config(name='set-expo-token', renderer='json')
def SetExpoToken(request):
    params = request.get_params(schemas.ExpoTokenSchema())
    device = get_device(request)
    device.expo_token = params['expo_token']
    return {}

@view_config(name='verify-account', renderer='json')
def verifyAccount(request):
    device = get_device(request)
    customer = device.customer
    return {'Verified': customer.verified_account}

@view_config(name='request-card', renderer='json')
def request_card(request):
    """Save the address a customer requested a new Ferly Card be mailed to."""
    params = request.get_params(schemas.AddressSchema())
    device = get_device(request)
    customer = device.customer
    usps_address_info_url = request.ferlysettings.usps_address_info_url
    usps_username = request.ferlysettings.usps_username
    if not usps_username:
        raise Exception("No USPS username is set")

    # Prepare the input fields for safe inclusion in XML. (Without escaping,
    # users may be able to trigger some vulnerability at USPS.)
    escaped = {}
    for k, v in params.items():
        escaped[k] = escape(v)

    # USPS uses Address1 as the more detailed part of the address, our line2.

    usps_request = (
        "API=Verify&XML="
        '<AddressValidateRequest USERID="{usps_username}"><Address ID="0">'
        "<Address1>{line2}</Address1><Address2>{line1}</Address2>"
        "<City>{city}</City><State>{state}</State><Zip5>{zip_code}</Zip5>"
        "<Zip4></Zip4></Address></AddressValidateRequest>").format(
        usps_username=usps_username, **escaped)
    try:
        response = requests.post(
            usps_address_info_url,
            data=usps_request,
            headers={'Content-Type': 'application/xml'})
        response.raise_for_status()
    except Exception:
        raise HTTPServiceUnavailable
    root = ElementTree.fromstring(response.content)
    if root.tag == 'AddressValidateResponse':
        address = root.find('Address')
        error = address.find('Error')
        if error:
            error_description = error.find('Description').text
            return {
                'error': 'invalid_address', 'description': error_description}
        else:
            line1 = getattr(address.find('Address2'), 'text', '')
            line2 = getattr(address.find('Address1'), 'text', '')
            city = getattr(address.find('City'), 'text', '')
            state = getattr(address.find('State'), 'text', '')
            zip5 = getattr(address.find('Zip5'), 'text', '')
            zip4 = getattr(address.find('Zip4'), 'text', '')
            zip_code = '{}-{}'.format(zip5, zip4)
            card_request = request.dbsession.query(CardRequest).filter(customer.id == CardRequest.customer_id).first()
            if card_request == None:
                new_card_request = CardRequest(
                    customer_id=customer.id, name=params['name'],
                    original_line1=params['line1'], original_line2=params['line2'],
                    original_city=params['city'], original_state=params['state'],
                    original_zip_code=params['zip_code'], line1=line1, line2=line2,
                    city=city, state=state, zip_code=zip_code, verified=params['verified']
                )
                request.dbsession.add(new_card_request)
            else:
                card_request.name=params['name']
                card_request.original_line1=params['line1']
                card_request.original_line2=params['line2']
                card_request.original_city=params['city']
                card_request.original_state=params['state']
                card_request.original_zip_code=params['zip_code']
                card_request.line1=line1
                card_request.line2=line2
                card_request.city=city
                card_request.state=state
                card_request.zip_code=zip_code
                card_request.verified=params['verified']
                card_request.downloaded=None
            return {
                'name': params['name'],
                'line1': line1,
                'line2': line2,
                'city': city,
                'state': state,
                'zip_code': zip_code
            }
    else:
        raise HTTPServiceUnavailable



@view_config(name='signup', renderer='json')
def add_individual(request):
    """Associate a device with a new customer and wallet."""
    params = request.get_params(schemas.OldSignupSchema())
    token = get_device_token(request, required=True)
    token_sha256 = hashlib.sha256(token.encode('utf-8')).hexdigest()
    expo_token = params['expo_token']
    os = params['os']
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.token_sha256 == token_sha256).first()
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

        device = Device(
            token_sha256=token_sha256,
            customer_id=new_customer.id,
            expo_token=expo_token,
            os=os)
        dbsession.add(device)
    return {}

@view_config(name='register', renderer='json')
def register(request):
    """Associate a device with a new customer and wallet."""
    params = request.get_params(schemas.RegisterSchema())
    token = get_device_token(request, required=True)
    token_sha256 = hashlib.sha256(token.encode('utf-8')).hexdigest()
    expo_token = params['expo_token']
    os = params['os']
    dbsession = request.dbsession
    username = params['username']
    wc_id = params['profile_id']
    first_name = params['first_name']
    last_name = params['last_name']
    new_customer = Customer(wc_id=wc_id, first_name=first_name,
                            last_name=last_name, username=username)
    new_customer.update_tsvector()
    dbsession.add(new_customer)
    dbsession.flush()

    device = Device(
        token_sha256=token_sha256,
        customer_id=new_customer.id,
        expo_token=expo_token,
        os=os)
    dbsession.add(device)
    return {}

@view_config(name='newSignup', renderer='json')
def signup(request):
    """Calls wingcash signup api."""
    params = request.get_params(schemas.SignupSchema())
    token = get_device_token(request)
    token_sha256 = hashlib.sha256(token.encode('utf-8')).hexdigest()
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.token_sha256 == token_sha256).first()
    if device is not None:
        return {'error': 'device_already_registered'}
    username = params['username']
    existing_customer = dbsession.query(Customer).filter(
        Customer.username == username).first()
    if existing_customer is not None:
        return {'error': 'existing_username'}
    else:
        postParams = {
            'client_id': request.ferlysettings.wingcash_client_id,
            'device_uuid': str(uuid.uuid5(uuid.NAMESPACE_URL, token)),
            'login': params['login'],
        }
        response = wc_contact(
            request,
            'POST',
            'aa/signup-closed',
            params=postParams,
            auth=True).json()
        if response.get('error') or response.get('invalid'):
            return response
        else:
            return { 
                'token': token,
                'attempt_path': response.get('attempt_path'), 
                'secret' : response.get('secret'), 
                'factor_id' : response.get('factor_id'), 
                'code_length' : response.get('code_length'),
                'revealed_codes' : response.get('revealed_codes')}


@view_config(name='auth-uid', renderer='json')
def auth_uid(request):
    """Calls wingcash auth-uid api."""
    params = request.get_params(schemas.AuthUidSchema())
    postParams = {
        'factor_id': params['factor_id'],
        'code': params['code'],
        'g-recaptcha-response': params['recaptcha_response']
    }
    response = wc_contact(
        request,
        'POST',
        params['attempt_path'] + 'auth-uid',
        secret=params['secret'],
        params=postParams, return_errors=True)
    response_json = response.json()
    if response.status_code != 200:
        if 'invalid' in response.json():
            raise Invalid(None, msg=response_json['invalid'])
        else:
            # Recaptcha required, or attempt expired
            error = response_json.get('error')
            if error == 'captcha_required':
                return recovery_error(request, 'recaptcha_required')
            else:
                return recovery_error(request, 'code_expired')
    return { 
            'profile_id': response_json.get('profile_id'), 
            'expo_token' : response_json.get('expo_token'), 
            'os' : response_json.get('os')}

@view_config(name='signup-finish', renderer='json')
def signup_finish(request):
    """Calls wingcash auth-uid api."""
    params = request.get_params(schemas.SignupFinishSchema())
    postParams = {
        'agreed': params['agreed'],
    }

    response = wc_contact(
        request,
        'POST',
        params['attempt_path'] + 'signup-finish',
        secret=params['secret'],
        params=postParams).json()
    if response.get('error') or response.get('invalid'):
        return response
    else:
        return {'profile_id': response.get('profile_id')}

@view_config(name='set-signup-data', renderer='json')
def set_signup_data(request):
    """Calls wingcash auth-uid api."""
    params = request.get_params(schemas.SetSignupDataSchema())
    postParams = {
        'first_name': params['first_name'],
        'last_name': params['last_name'],
    }
    response = wc_contact(
        request,
        'POST',
        params['attempt_path'] + 'set-signup-data',
        secret=params['secret'],
        params=postParams).json() 
    if response.get('error') or response.get('invalid'):
        return response
    else:
        return {}

@view_config(name='is-customer', renderer='json')
def is_customer(request):
    """Return {'is_customer': true} if the device token is for a customer."""
    params = request.get_params(schemas.IsCustomerSchema())
    if params['expected_env'] != request.ferlysettings.environment:
        return {'error': 'unexpected_environment'}
    token = get_device_token(request, required=True)
    token_sha256 = hashlib.sha256(token.encode('utf-8')).hexdigest()
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.token_sha256 == token_sha256).first()
    # Doing more than this requires updating device.last_used to models.now_utc
    return {'is_customer': device is not None}


@view_config(name='profile', renderer='json')
def profile(request):
    """Describe the profile currently associated with a device."""
    device = get_device(request)
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
            design_object = serialize_design(request, design)
            design_object.update({
                'amount': loop['amount'],
                'expiring': loop['expiring'],
            })
            amounts.append(design_object)

    recents = [dbsession.query(
        Customer).get(recent) for recent in customer.recents]
    
    if len(amounts) > 0 and not customer.verified_account:
        customer.verified_account = True
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
    device = get_device(request)
    customer = device.customer
    recipient_id = params['recipient_id']
    design_id = params['design_id']
    amount = params['amount']
    message = params['message']
    name = params['name']
    invitation_type = params.get('invitation_type','')
    invitation_code_length = params.get('invitation_code_length')
    dbsession = request.dbsession
    sendNotify = False
    customer_uid = 'wingcash:{0}'.format(customer.wc_id)
    if params.get('sender','') == '':
        recipient = dbsession.query(Customer).get(recipient_id)
        if recipient:
            sendNotify = True
            recipient_uid = 'wingcash:{0}'.format(recipient.wc_id)
        else:
            recipient = recipient_id
            recipient_uid = recipient

    else:
        recipient = recipient_id
        recipient_uid = recipient
    design = dbsession.query(Design).get(design_id)
    if design is None:
        return {'error': 'invalid_design'}
    amount_row = "{0}-USD-{1}".format(design.wc_id, amount)
    params = {
        'sender_uid': customer_uid,
        'recipient_uid': recipient_uid,
        'amounts': amount_row,
        'require_recipient_email': False,
        'accepted_policy': True,
        'appdata.ferly.transactionType': 'gift',
        'appdata.ferly.designId': design_id,
        'appdata.ferly.title': design.title,
        'appdata.ferly.name': name
    }

    if invitation_type != '':
        params['invitation_type'] = invitation_type
        params['invitation_code_length'] = invitation_code_length
        params['invitation_expire_days'] = 30
    if message:
        params['message'] = message

    # Add recipient_id to customer.recents.
    new_recents = [recipient_id]
    new_recents.extend(
        filter(lambda x: x != recipient_id, customer.recents or ()))
    access_token = get_wc_token(request, customer)
    response = wc_contact(request, 'POST', 'wallet/send', params=params,
               access_token=access_token).json()
    completed = response.get('transfer')
    if completed and not sendNotify:
        completed = completed.get('completed') 
        if completed:
            completed = response.get('transfer')
            id = completed.get('recipient_id')
            recipient = dbsession.query(Customer).filter(Customer.wc_id == id).first()
            sendNotify = True
            recipient_id = recipient.id
            new_recents = [recipient_id]
            new_recents.extend(
                filter(lambda x: x != recipient_id, customer.recents or ()))
    formatted_amount = '${:.2f}'.format(amount)
    title = 'Received {0} {1}'.format(formatted_amount, design.title)
    sender = 'from {0}'.format(customer.title)
    body = '{0}\n{1}'.format(message, sender) if message else sender
    if sendNotify:
        data={
            'type': 'receive',
            'from': customer.first_name+' '+customer.last_name,
            'amount': formatted_amount, 
            'title': design.title,
            'message': message
        }
        notify_customer(
            request, recipient, title, body, channel_id='gift-received',data=data)
        customer.recents = new_recents[:9]   
    response.pop("profile", None)
    return response


@view_config(name='edit-profile', renderer='json')
def edit_profile(request):
    """Update a customer's profile information"""
    params = request.get_params(schemas.EditProfileSchema())
    device = get_device(request)
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


def get_loop_id_from_transfer(transfer):
    try:
        # Display the design from the first closed loop movement, if any.
        for movement in transfer['movements']:
            for loop in movement['loops']:
                if loop['loop_id'] != '0':
                    return loop['loop_id']
    except Exception:
        log.exception(
            "Failed to parse movements from transfer %s", transfer['id'])
    return None


@view_config(name='history', renderer='json')
def history(request):
    """Request and return the customer's WingCash transfer history."""
    params = request.get_params(schemas.HistorySchema())
    device = get_device(request)
    customer = device.customer
    dbsession = request.dbsession
    post_params = {'limit': params['limit'], 'offset': params['offset']}

    access_token = get_wc_token(request, customer)
    response = wc_contact(
        request, 'GET', 'wallet/history', params=post_params,
        access_token=access_token)
    json2 = response.json()
    results = json2.get('results', [])
    has_more = bool(json2.get('more'))
    history = []
    # Gather the designs using a single query for speed.
    all_loop_ids = set()
    transfer_loop_ids = {}  # {transfer_id: loop_id}
    for transfer in results:
        loop_id = get_loop_id_from_transfer(transfer)
        if loop_id:
            all_loop_ids.add(loop_id)
        transfer_loop_ids[transfer['id']] = loop_id
    if all_loop_ids:
        rows = (
            dbsession.query(Design)
            .filter(Design.wc_id.in_(all_loop_ids))
            .all())
        designs = {row.wc_id: row for row in rows}
    else:
        designs = {}
    for transfer in results:
        appdataDesignId = transfer.get('appdata.ferly.designId')
        pending = transfer.get('next_activity')
        amount = transfer['amount']
        timestamp = transfer['timestamp']
        loop_id = transfer_loop_ids.get(transfer['id'])
        if loop_id:
            design = designs.get(loop_id)
        elif appdataDesignId:
            design =  dbsession.query(Design).filter(Design.id == appdataDesignId).first()
        else:
            design = None
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
                if pending == "invite.wait":
                    transfer_type = 'pending'
                elif transfer.get('canceled') == True:
                    transfer_type = 'canceled'
                else:
                    transfer_type = 'send'
            else:
                transfer_type = 'redeem'
        design_json = (
            None if design is None else serialize_design(request, design))
        history.append({
            'id': transfer['id'],
            'sent_count': transfer.get('sent_count'),
            'name': transfer.get('appdata.ferly.name'),
            'amount': amount,
            'transfer_type': transfer_type,
            'counter_party': counter_party,
            'design': design_json,
            # NOTE: design_title and design_logo_image_url are deprecated in
            # favor of the design attribute. They will be removed soon.
            'design_title': 'Unrecognized' if design is None else design.title,
            'design_logo_image_url': (
                '' if design is None else design.logo_image_url),
            'timestamp': timestamp,
            # 'loop_id': loop_id
        })
    return {'history': history, 'has_more': has_more}


@view_config(name='transfer', renderer='json')
def transfer(request):
    """Request and return WingCash transfer details of a transfer."""
    params = request.get_params(schemas.TransferSchema())
    device = get_device(request)
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
        # Note: Refusing permission here may be overzealous.
        # OPN automatically applies transfer view policies that allow view
        # access only to transfers in which the viewer is a stakeholder.
        # There are more stakeholder roles than just sender and recipient.
        return {'error': 'permission_denied'}

    profile_image_url = ''
    # Note: sender_info and/or recipient_info is not always available.
    # For example, sometimes the recipient has not yet created a wallet.
    if bool(counter_party and counter_party['is_individual']):
        cp_customer = dbsession.query(Customer).filter(
            Customer.wc_id == counter_party['uid_value']).first()
        if cp_customer is not None:
            profile_image_url = cp_customer.profile_image_url
    return {
        'card_acceptor': transfer.get('card_acceptor'),
        'pan_redacted': transfer.get('pan_redacted'),
        'available_amount': transfer.get('available_amount'),
        'reason': transfer.get('reason'),
        'expiration': transfer.get('alarms'),
        'convenience_fee': transfer.get('appdata.ferly.convenience_fee', ''),
        'cc_brand': transfer.get('appdata.ferly.stripe_brand', ''),
        'cc_last4': transfer.get('appdata.ferly.stripe_last4', ''),
        'message': transfer['message'],
        'counter_party_profile_image_url': profile_image_url
    }

@view_config(name='search-customers', renderer='json')
def search_customers(request):
    """Search the list of customers"""
    params = request.get_params(schemas.SearchCustomersSchema())
    dbsession = request.dbsession
    device = get_device(request)
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
    device = get_device(request)
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
    customer.profile_image_url = s3Url.strip('/') + '/' + bucket_name + '/' +  new_file_name

    return {}

@view_config(name='delete-device-tokens', renderer='json')
def deleteDeviceTokens(request):
    """Delete old device"""
    dbsession = request.dbsession
    device = get_device(request)
    dbsession.query(Device).filter(device.id == Device.id).delete()
    return {}

@view_config(name='get-expo-token', renderer='json')
def getExpoToken(request):
    """Get current expo token"""
    device = get_device(request)
    return {'expo_token': device.expo_token}


@view_config(name='log-info', renderer='json')
def logInfo(request):
    """Log client info"""
    params = request.get_params(schemas.LogInfoSchema())
    device = get_device(request)
    log.info("device" + ": " + device.id + ", " + device.customer.id + ": " + params['text'])
    return {}

@view_config(name='log-info-initial', renderer='json')
def logInfoInitial(request):
    """Log client info"""
    params = request.get_params(schemas.LogInfoSchema())
    log.info(get_device_token(request) + ": " + params['text'])
    return {}

@view_config(name='get-customer-name', renderer='json')
def getCustomerName(request):
    """Gets the customer name"""
    params = request.get_params(schemas.GetCustomerNameSchema())
    id = params.get('recipient_id')
    device = get_device(request)
    if device:
        recipient = request.dbsession.query(Customer).filter(Customer.wc_id == id).first()
        if recipient:
            return {'name' : (recipient.first_name + ' ' + recipient.last_name)}
        else:
            return {'invalid': 'Recipient is not a Ferly Customer'}