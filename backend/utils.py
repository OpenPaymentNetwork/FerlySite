from backend.models.models import Device
from backend.models.models import now_utc
from pyramid.httpexceptions import HTTPUnauthorized
import requests
import json


def get_device(request, params):
    device_id = params.get('device_id')
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    if device is None or device.user is None:
        raise HTTPUnauthorized
    device.last_used = now_utc
    return device


def get_params(request, schema):
    if getattr(request, 'content_type', None) == 'application/json':
        param_map = request.json_body
    else:
        param_map = request.params
    return schema.bind(request=request).deserialize(param_map)


def notify_user(request, user, title, body, channel_id=None):
    url = 'https://exp.host/--/api/v2/push/send'
    devices = request.dbsession.query(Device).filter(
        Device.user_id == user.id).all()

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
