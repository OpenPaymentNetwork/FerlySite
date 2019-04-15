from backend.database.models import Device
from backend.database.models import now_utc
from backend.wccontact import wc_contact
from pyramid.httpexceptions import HTTPUnauthorized
import requests
import json


def get_device(request, params):
    device_id = params.get('device_id')
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    if device is None or device.customer is None:
        raise HTTPUnauthorized
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
        requests.post(url, data=json.dumps(notifications), headers=headers)


def get_wc_token(request, customer, permissions=[]):
    params = {
        'uid': 'wingcash:' + customer.wc_id,
        'concurrent': True,
        'permissions': permissions
    }
    response = wc_contact(request, 'GET', 'p/token', params, auth=True)
    return response.json().get('access_token')
