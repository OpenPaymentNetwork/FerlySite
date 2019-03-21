from backend import schema
from backend.models.models import Design
from backend.models.models import Device
from backend.models.models import User
from backend.serialize import serialize_user
from backend.utils import get_device
from backend.utils import notify_user
from backend.wccontact import get_wc_token
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
    """Associate a device with a new user and wallet."""
    params = request.get_params(schema.RegisterSchema())
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
        existing_user = dbsession.query(User).filter(
            User.username == username).first()

        if existing_user is not None:
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
        user = User(wc_id=wc_id, first_name=first_name, last_name=last_name,
                    username=username)
        user.update_tsvector()
        dbsession.add(user)
        dbsession.flush()

        device = Device(device_id=device_id, user_id=user.id,
                        expo_token=expo_token, os=os)
        dbsession.add(device)
    return {}


@view_config(name='is-user', renderer='json')
def is_user(request):
    """Return if the device_id is associated with a user."""
    params = request.get_params(schema.IsUserSchema())
    env = 'production' if params['expected_env'] == 'production' else 'staging'
    if env != request.ferlysettings.environment:
        return {'error': 'unexpected_environment'}
    device_id = params['device_id']
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    # Doing more than this requires updating device.last_used to models.now_utc
    return {'is_user': device is not None}


@view_config(name='profile', renderer='json')
def profile(request):
    """Describe the profile currently associated with a device."""
    params = request.get_params(schema.DeviceSchema())
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    access_token = get_wc_token(request, user)
    response = wc_contact(request, 'GET', 'wallet/info',
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
                'wallet_url': design.wallet_url,
                'logo_url': design.image_url})

    recents = [dbsession.query(User).get(recent) for recent in user.recents]

    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'profileImage': user.image_url,
        'amounts': amounts,
        'uids': uids,
        'recents': [serialize_user(request, u) for u in recents]
    }


@view_config(name='send', renderer='json')
def send(request):
    """Send Closed Loop Cash to another Ferly user."""
    params = request.get_params(schema.SendSchema())
    device = get_device(request, params)
    user = device.user

    recipient_id = params['recipient_id']
    design_id = params['design_id']
    amount = params['amount']
    message = params['message']

    dbsession = request.dbsession
    recipient = dbsession.query(User).get(recipient_id)
    design = dbsession.query(Design).get(design_id)
    amount_row = "{0}-USD-{1}".format(design.wc_id, amount)

    params = {
        'sender_id': user.wc_id,
        'recipient_uid': 'wingcash:{0}'.format(recipient.wc_id),
        'amounts': amount_row,
        'require_recipient_email': False,
        'accepted_policy': True
    }

    if message:
        params['message'] = message

    user.recents.add(recipient.id)

    access_token = get_wc_token(request, user)
    wc_contact(request, 'POST', 'wallet/send', params=params,
               access_token=access_token)

    formatted_amount = '${:.2f}'.format(amount)

    title = 'Received {0} {1}'.format(formatted_amount, design.title)
    sender = 'from {0}'.format(user.title)
    body = '{0}\n{1}'.format(message, sender) if message else sender
    notify_user(request, recipient, title, body, channel_id='gift-received')

    return {}


@view_config(name='edit-profile', renderer='json')
def edit_profile(request):
    """Update a user's profile information"""
    params = request.get_params(schema.EditProfileSchema())
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    first_name = params['first_name']
    last_name = params['last_name']
    username = params['username']
    existing_user = dbsession.query(User).filter(
        User.username == username).first()

    if existing_user is not None and existing_user is not user:
        return {'error': 'existing_username'}
    else:
        if first_name != user.first_name or last_name != user.last_name:
            post_params = {
                'first_name': first_name,
                'last_name': last_name
            }
            access_token = get_wc_token(request, user)
            wc_contact(request, 'POST', 'wallet/change-name',
                       params=post_params, access_token=access_token)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.update_tsvector()
    return {}


@view_config(name='history', renderer='json')
def history(request):
    """Request and return the user's WingCash transfer history."""
    params = request.get_params(schema.HistorySchema())
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    post_params = {'limit': params['limit'], 'offset': params['offset']}

    access_token = get_wc_token(request, user)
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
        image_url = ''
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
                image_url = design.image_url

        sender_info = transfer['sender_info']
        recipient_info = transfer['recipient_info']
        transfer_type = 'unrecognized'
        counter_party = ''
        if transfer['recipient_id'] == user.wc_id:
            counter_party = sender_info['title']
            if not bool(sender_info['is_individual']):
                transfer_type = 'purchase'
            else:
                transfer_type = 'receive'
        elif transfer['sender_id'] == user.wc_id:
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
            'design_image_url': image_url,
            'timestamp': timestamp,
            # 'loop_id': loop_id
        })
    return {'history': history, 'has_more': has_more}


@view_config(name='transfer', renderer='json')
def transfer(request):
    """Request and return WingCash transfer details of a transfer."""
    params = request.get_params(schema.TransferSchema())
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    access_token = get_wc_token(request, user)
    transfer = wc_contact(
        request,
        'GET',
        't/{0}'.format(params['transfer_id']),
        access_token=access_token).json()

    sender_info = transfer['sender_info']
    recipient_info = transfer['recipient_info']
    if transfer['recipient_id'] == user.wc_id:
        counter_party = sender_info
    elif transfer['sender_id'] == user.wc_id:
        counter_party = recipient_info
    else:
        return {'error': 'permission_denied'}

    image_url = ''
    #  is_individual may not always be accurate, according to WingCash.
    if bool(counter_party['is_individual']):
        cp_user = dbsession.query(User).filter(
            User.wc_id == counter_party['uid_value']).first()
        if cp_user is not None:
            image_url = cp_user.image_url

    return {
        'message': transfer['message'],
        'counter_party_image_url': image_url
    }


@view_config(name='search-users', renderer='json')
def search_users(request):
    """Search the list of users"""
    params = request.get_params(schema.SearchUsersSchema())
    dbsession = request.dbsession
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    # Create an expression that converts the query
    # to a prefix match filter on the design table.
    text_parsed = func.regexp_replace(
        cast(func.plainto_tsquery(params['query']), Unicode),
        r"'( |$)", r"':*\1", 'g')

    users = dbsession.query(User).filter(
        User.tsvector.match(text_parsed),
        User.id != user.id).order_by(User.username)

    return {'results': [serialize_user(request, x) for x in users]}


@view_config(name='upload-profile-image', renderer='json')
def upload_profile_image(request):
    """Allow a user to upload an image for their profile picture"""
    params = request.get_params(schema.UploadProfileImageSchema())
    device = get_device(request, params)
    user = device.user
    image = params['image']
    content_type = image.type
    file_type = content_type.split('/')[-1]

    access_key_id = request.ferlysettings.aws_access_key_id
    secret_key = request.ferlysettings.aws_secret_key
    new_file_name = '{0}|{1}.{2}'.format(
        user.id, str(uuid.uuid4()), file_type)
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

    current_image = user.image_url
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
    user.image_url = os.path.join(s3Url, bucket_name, new_file_name)

    return {}
