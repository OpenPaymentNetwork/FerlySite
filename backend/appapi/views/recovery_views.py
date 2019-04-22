from backend.appapi.schemas import recovery_views_schemas as schemas
from backend.database.models import Device
from backend.database.models import Customer
from backend.appapi.utils import get_device
from backend.appapi.utils import get_wc_token
from backend.wccontact import wc_contact
from colander import Invalid
from pyramid.view import view_config


@view_config(name='recover', renderer='json')
def recover(request):
    params = request.get_params(schemas.RecoverySchema())

    wc_params = {'login': params['login'], 'device_uuid': params['device_id']}
    response = wc_contact(request, 'POST', 'aa/signin-closed', auth=True,
                          params=wc_params, return_errors=True)
    response_json = response.json()

    invalid_response = Invalid(
        None, msg={'login': "Invalid email address or phone number."})
    if 'invalid' in response_json:
        raise invalid_response

    # must have not completed_mfa and must have factor_id else: unsupported
    mfa = response_json.get('completed_mfa')
    factor_id = response_json.get('factor_id', False)
    if mfa or not factor_id:
        return {'error': 'unexpected_auth_attempt'}
    unauthenticated = response_json['unauthenticated']
    login_type = [x.split(':')[0] for x in unauthenticated.keys()][0]
    if login_type == 'username':
        raise invalid_response

    r = {'login_type': login_type}
    for key in response_json:
        if key in (
            'secret',
            'attempt_path',
            'code_length',
            'factor_id',
            'revealed_codes',
        ):
            r[key] = response_json[key]
    return r


@view_config(name='recover-code', renderer='json')
def recover_code(request):
    params = request.get_params(schemas.RecoveryCodeSchema())
    dbsession = request.dbsession

    device_id = params['device_id']
    expo_token = params['expo_token']
    os = params['os']
    device = dbsession.query(Device).filter(
        Device.device_id == device_id).first()
    if device:
        # Trying to recover a device in use
        return {'error': 'unexpected_auth_attempt'}
    wc_params = {
        'code': params['code'],
        'factor_id': params['factor_id'],
        'g-recaptcha-response': params['recaptcha_response']
    }

    urlTail = params['attempt_path'] + '/auth-uid'
    response = wc_contact(request, 'POST', urlTail, secret=params['secret'],
                          params=wc_params, return_errors=True)
    response_json = response.json()

    if response.status_code != 200:
        if 'invalid' in response.json():
            raise Invalid(None, msg=response_json['invalid'])
        else:
            # Recaptcha required, or attempt expired
            error = response_json.get('error')
            if error == 'captcha_required':
                return {'error': 'recaptcha_required'}
            else:
                return {'error': 'code_expired'}
    mfa = response_json.get('completed_mfa', False)
    profile_id = response_json.get('profile_id')
    if not mfa or profile_id is None:
        return {'error': 'unexpected_auth_attempt'}

    wc_id = profile_id
    customer = dbsession.query(Customer).filter(Customer.wc_id == wc_id).one()

    new_device = Device(device_id=device_id, customer_id=customer.id,
                        expo_token=expo_token, os=os)
    dbsession.add(new_device)

    return {}


@view_config(name='add-uid', renderer='json')
def add_uid(request):
    """Associate an email or phone number with a customer's profile"""
    params = request.get_params(schemas.AddUIDSchema())
    device = get_device(request, params)
    customer = device.customer

    wc_params = {
        'login': params['login'],
        'uid_type': params['uid_type']
    }

    access_token = get_wc_token(request, customer)
    response = wc_contact(request, 'POST', 'wallet/add-uid', params=wc_params,
                          access_token=access_token)
    response_json = response.json()
    r = {}
    for key in response_json:
        if key in ('secret', 'code_length', 'revealed_codes', 'attempt_id'):
            r[key] = response_json[key]
    return r


@view_config(name='confirm-uid', renderer='json')
def confirm_uid(request):
    params = request.get_params(schemas.AddUIDCodeSchema())
    device = get_device(request, params)
    customer = device.customer

    wc_params = {
        'secret': params['secret'],
        'code': params['code'],
        'attempt_id': params['attempt_id'],
        'g-recaptcha-response': params['recaptcha_response']
    }
    if params.get('replace_uid'):
        wc_params['replace_uid'] = params['replace_uid']

    access_token = get_wc_token(request, customer)
    response = wc_contact(
        request, 'POST', 'wallet/add-uid-confirm', params=wc_params,
        access_token=access_token, return_errors=True)

    if response.status_code != 200:
        if 'invalid' in response.json():
            raise Invalid(None, msg=response.json()['invalid'])
        else:
            # Recaptcha required, or attempt expired
            error = response.json().get('error')
            if error == 'captcha_required':
                return {'error': 'recaptcha_required'}
            elif response.status_code == 410:
                return {'error': 'code_expired'}
            else:
                return {'error': 'unexpected_wc_response'}
    return {}
