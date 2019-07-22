
from backend.database.models import StaffToken
from backend.site import StaffSite
import cognitojwt
from cryptography.fernet import Fernet
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
import datetime
import hashlib
import json
import logging
import requests
import urllib.parse

log = logging.getLogger(__name__)


def get_redirect_uri(request, staff_site):
    return request.resource_url(staff_site, 'cognito-cb')


@view_config(
    name='login',
    context=StaffSite)
def login(staff_site, request):
    """Redirect to Amazon Cognito login"""
    settings = request.ferlysettings
    qs = urllib.parse.urlencode([
        ('response_type', 'code'),
        ('client_id', settings.cognito_client_id),
        ('redirect_uri', get_redirect_uri(request, staff_site)),
    ])

    url = 'https://%s/login?%s' % (settings.cognito_domain, qs)
    return HTTPSeeOther(url)


@view_config(
    name='cognito-cb',
    context=StaffSite,
    renderer='templates/cognito_cb.pt')
def cognito_callback(staff_site, request):
    """Receive an OAuth code, add a StaffToken, and redirect."""
    settings = request.ferlysettings
    code = request.params.get('code')
    if not code or len(code) > 100:
        raise HTTPBadRequest()

    token_url = 'https://%s/oauth2/token' % settings.cognito_domain
    token_data = [
        ('grant_type', 'authorization_code'),
        ('client_id', settings.cognito_client_id),
        ('code', code),
        ('redirect_uri', get_redirect_uri(request, staff_site)),
    ]

    resp = requests.post(
        token_url,
        auth=(settings.cognito_client_id, settings.cognito_client_secret),
        data=token_data)
    resp.raise_for_status()
    tokens_json = resp.json()
    assert 'access_token' in tokens_json
    assert 'refresh_token' in tokens_json

    verified_claims = cognitojwt.decode(
        tokens_json['id_token'],
        settings.cognito_region,
        settings.cognito_userpool_id,
        app_client_id=settings.cognito_client_id,
    )

    # access_token = tokens_json['access_token']

    # info_url = 'https://%s/oauth2/userInfo' % settings.cognito_domain
    # resp = requests.get(
    #     info_url, headers={
    #         'Authorization': 'Bearer %s' % access_token,
    #     })
    # resp.raise_for_status()
    # user_info = resp.json()
    # log.info("Staff login user_info: %s", user_info)

    username = verified_claims['cognito:username']
    groups = verified_claims['cognito:groups']

    secret = Fernet.generate_key()
    secret_sha256 = hashlib.sha256(secret).hexdigest()
    tokens_encoded = json.dumps(tokens_json).encode('utf-8')
    tokens_fernet = Fernet(secret).encrypt(tokens_encoded).decode('ascii')

    now = datetime.datetime.utcnow()
    st = StaffToken(
        secret_sha256=secret_sha256,
        tokens_fernet=tokens_fernet,
        update_ts=now + datetime.timedelta(
            seconds=settings.token_trust_duration),
        expires=now + datetime.timedelta(
            seconds=settings.token_duration),
        user_agent=request.user_agent,
        remote_addr=request.remote_addr,
        username=username,
        groups=groups,
        id_claims=verified_claims,
    )
    request.dbsession.add(st)
    request.dbsession.flush()  # Assign st.id

    cookie_value = '%s-%s' % (st.id, secret.decode('ascii'))

    location = request.resource_url(staff_site)
    request.response.set_cookie(
        'staff_token',
        cookie_value,
        path=request.resource_path(staff_site),
        secure=settings.secure_cookie,
        httponly=True,
        max_age=datetime.timedelta(days=365))

    delete_old_tokens(request)

    return {'location': location}


@view_config(
    name='logout',
    context=StaffSite,
    renderer='templates/logout.pt')
def logout(staff_site, request):
    """Unset the staff_token cookie."""
    settings = request.ferlysettings
    request.response.set_cookie(
        'staff_token',
        '',
        path=request.resource_path(staff_site),
        secure=settings.secure_cookie,
        httponly=True)
    return {}


def delete_old_tokens(request):
    expire_time = datetime.datetime.utcnow() - datetime.timedelta(
        days=request.ferlysettings.token_delete_days)
    q = request.dbsession.query(StaffToken)
    q.filter(StaffToken.expires <= expire_time).delete()
