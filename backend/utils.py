from backend.models.models import Device
from pyramid.httpexceptions import HTTPUnauthorized
import requests


# TODO remove params argument - don't. must unbind in view first
def get_device(request, params):
    device_id = params.get('device_id')
    dbsession = request.dbsession
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    if device is None or device.user is None:
        raise HTTPUnauthorized
    return device


def get_params(request):
    if getattr(request, 'content_type', None) == 'application/json':
        return request.json_body
    else:
        return request.params


def notify_user(user, title, body):
    url = 'https://exp.host/--/api/v2/push/send'
    token = user.expo_token
    # has expo_token?
    r = requests.post(url, data={'to': token, 'title': title, 'body': body})
    # r.raise_for_status()
    return r

