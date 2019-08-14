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


def get_device_token(request, params, required=False):
    # First try the preferred method of getting the device token: the
    # Authorization header.
    token = None

    header = request.headers.get('Authorization')
    if header:
        header = header.strip()
        if header.startswith('Bearer '):
            token = header[7:].lstrip()

    if not token:
        # For backward compat, accept the device token as a parameter
        # called device_id. Accepting the device token this way is a security
        # issue for at least two reasons:
        #
        # 1. The token may be transmitted with other parameters
        #    in compressed form, enabling a BREACH or CRIME attack.
        # 2. If the request is a GET, the token will be logged,
        #    making access logs valuable for attackers.
        #
        # Transmission of device tokens in the Authorization header
        # instead avoids these issues.
        token = params.get('device_id')

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
        raise HTTPBadRequest(json={
            'error': 'device_token_required',
        })

    return None


def get_device(request, params):
    """Authenticate a device."""
    token = get_device_token(request, params)
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


def notify_customer(request, customer, title, body, channel_id=None):
    url = 'https://exp.host/--/api/v2/push/send'
    devices = request.dbsession.query(Device).filter(
        Device.customer_id == customer.id).all()

    notifications = []
    for device in devices:
        if device.expo_token:
            notification = {
                'to': device.expo_token,
                'title': title,
                'body': body,
                'sound': 'default'
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


def get_wc_token(request, customer, permissions=[]):
    params = {
        'uid': 'wingcash:' + customer.wc_id,
        'concurrent': True,
        'permissions': permissions
    }
    response = wc_contact(request, 'GET', 'p/token', params, auth=True)
    try:
        response.raise_for_status()
    except Exception:
        log.exception(
            "Error while getting access token from OPN: %s",
            repr(response.text))
        # Propagate the error.
        raise
    return response.json().get('access_token')
