from backend.database.models import Device
from backend.database.models import now_utc
from backend.wccontact import wc_contact
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPUnauthorized
import datetime
import hashlib
import logging
import requests

log = logging.getLogger(__name__)

min_device_token_length = 32
max_device_token_length = 200

def recovery_error(request, msg):
    log.warning(
        "Recovery error %s for IP address %s",
        repr(msg), getattr(request, 'remote_addr', None))
    return {'error': msg}

def get_device_token(request, required=False):
    # First try the preferred method of getting the device token: the
    # Authorization header.
    token = None
    header = request.headers.get('Authorization')
    if header:
        header = header.strip()
        if header.startswith('Bearer '):
            token = header[7:].lstrip()

    if (token and
            len(token) >= min_device_token_length and
            len(token) <= max_device_token_length):
        return token

    if required:
        if token and len(token) < min_device_token_length:
            raise HTTPBadRequest(json={
                'error': 'device_token_too_short',
            })
        if token and len(token) > max_device_token_length:
            raise HTTPBadRequest(json={
                'error': 'device_token_too_long',
            })
        log.error("Device token missing from request: %s", request)
        raise HTTPBadRequest(json={
            'error': 'device_token_required',
        })
    else:
        import math
        import random
        result = ''
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        charactersLength = len(characters)
        for i in range(32):
            result += characters[math.floor(random.uniform(0,1) * charactersLength)]
        return result

    return None


def get_device(request):
    """Authenticate a device."""
    token = get_device_token(request)
    if not token:
        raise HTTPUnauthorized()
    token_sha256 = hashlib.sha256(token.encode('utf-8')).hexdigest()

    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.token_sha256 == token_sha256).first()
    if device is None:
        raise HTTPUnauthorized()
    now = datetime.datetime.utcnow()
    # If at least 5 minutes have passed since the last use of this device,
    # update last_used. We avoid doing this on every request because
    # database writes can be much more expensive than reads.
    if now - device.last_used >= datetime.timedelta(seconds=5 * 60):
        device.last_used = now_utc
    return device


def notify_customer(request, customer, title, body, channel_id=None, data={}):
    url = 'https://exp.host/--/api/v2/push/send'
    rows = request.dbsession.query(Device.expo_token).distinct(Device.expo_token).filter(
        Device.customer_id == customer.id).all()
    expoTokens = [x for (x,) in rows]
    notifications = []
    for expoToken in expoTokens:
        if expoToken:
            notification = {
                'to': expoToken,
                'title': title,
                'body': body,
                'sound': 'default',
                'data' : data
            }
            if channel_id:
                notification['channelId'] = channel_id
            notifications.append(notification)

    if notifications:
        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/json',
        }
        response = requests.post(
            url, json=notifications, headers=headers)
        try:
            response.raise_for_status()
        except Exception:
            log.exception(
                "Error while notifying customer %s, title %s: %s",
                repr(customer.id), repr(title), repr(response.text))


def get_wc_token(request, customer, permissions=[], open_loop=False):
    params = {
        'uid': 'wingcash:' + customer.wc_id,
        'concurrent': True,
        'permissions': permissions
    }
    response = wc_contact(request, 'POST', 'p/token', params, auth=True, open_loop=open_loop)
    try:
        response.raise_for_status()
    except Exception:
        log.exception(
            "Error while getting access token from OPN for customer %s: %s",
            customer.id, repr(response.text))
        # Propagate the error.
        raise
    return response.json().get('access_token')
