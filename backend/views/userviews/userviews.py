from backend import schema
from backend.models.models import Design
from backend.models.models import Device
from backend.models.models import User
from backend.utils import get_device
from backend.utils import get_params
from backend.utils import notify_user
from backend.wccontact import get_wc_token
from backend.wccontact import wc_contact
from pyramid.view import view_config


@view_config(name='signup', renderer='json')
def signup(request):
    """Associate a device with a new user and wallet."""
    param_map = get_params(request)
    params = schema.RegisterSchema().bind(
        request=request).deserialize(param_map)
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
        dbsession.add(user)
        dbsession.flush()

        device = Device(device_id=device_id, user_id=user.id,
                        expo_token=expo_token, os=os)
        dbsession.add(device)
    return {}


@view_config(name='is-user', renderer='json')
def is_user(request):
    """Return if the device_id is associated with a user."""
    param_map = get_params(request)
    params = schema.DeviceSchema().bind(request=request).deserialize(param_map)
    device_id = params['device_id']
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    response = {'is_user': device is not None}
    # Doing more than this requires updating device.last_used to models.now_utc
    return response


@view_config(name='wallet', renderer='json')
def wallet(request):  # TODO rename as profile
    """Describe the profile currently associated with a device."""
    param_map = get_params(request)
    params = schema.DeviceSchema().bind(request=request).deserialize(param_map)
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
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'profileImage': user.image_url,
        'amounts': amounts,
        'uids': uids
    }


@view_config(name='send', renderer='json')
def send(request):
    """Send Closed Loop Cash to another Ferly user."""
    param_map = get_params(request)
    params = schema.SendSchema().bind(request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user

    recipient_id = params['recipient_id']
    design_id = params['design_id']
    amount = params['amount']

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

    access_token = get_wc_token(request, user)
    wc_contact(request, 'POST', 'wallet/send', params=params,
               access_token=access_token)

    # formatted_amount = '${:.2f}'.format(amount)

    # title = 'Gift Received!'
    # body = 'You have received {0} {1} from {2}'.format(
    #         formatted_amount, design.title, user.title)
    # notify_user(recipient, title, body)

    # title = 'Gift Sent!'
    # body = 'You have sent ${:.2f} {1} to {2}'.format(
    #         amount, design.title, recipient.title)
    # notify_user(user, title, body)

    return {
        # new wallet, profile object . title
    }


@view_config(name='edit-profile', renderer='json')
def edit_profile(request):
    """Update a user's profile information"""
    param_map = get_params(request)
    params = schema.EditProfileSchema().bind(
        request=request).deserialize(param_map)
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
    return {}


@view_config(name='history', renderer='json')
def history(request):
    """Request and return the user's WingCash transfer history."""
    param_map = get_params(request)
    params = schema.HistorySchema().bind(
        request=request).deserialize(param_map)
    device = get_device(request, params)
    user = device.user
    dbsession = request.dbsession

    post_params = {'limit': params['limit'], 'offset': params['offset']}

    access_token = get_wc_token(request, user)
    response = wc_contact(
        request, 'GET', 'wallet/history', params=post_params,
        access_token=access_token)

    results = response.json()['results']
    has_more = bool(response.json()['more'])
    history = []
    for transfer in results:
        amount = transfer['amount']
        timestamp = transfer['timestamp']
        title = 'Unrecognized'
        transfer_type = 'unrecognized'
        try:
            # TODO Make sure all loop_ids are the same
            first_movement_loop = transfer['movements'][0]['loops'][0]
            loop_id = first_movement_loop['loop_id']
            # TODO Get CLC title from memcache by loop_id or call wingcash and
            # cache it in parallel
            design = dbsession.query(Design).filter(
                Design.wc_id == loop_id).first()
            if (design):
                title = design.title
        except Exception:
            # No money was moved. ie waiting or canceled transfer
            pass

        sender_info = transfer['sender_info']
        recipient_info = transfer['recipient_info']
        if transfer['workflow_type'] == 'purchase_offer':
            transfer_type = 'purchase'
            amount = first_movement_loop['amount']
            counter_party = sender_info['title']
        elif transfer['recipient_id'] == user.wc_id:
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
            'amount': amount,
            'transfer_type': transfer_type,
            'counter_party': counter_party,
            'title': title,
            'timestamp': timestamp,
            # 'loop_id': loop_id
        })
    return {'history': history, 'has_more': has_more}
