
from backend.database.models import StaffToken
from cryptography.fernet import Fernet
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPSeeOther
import datetime
import hashlib
import hmac
import json
import logging
import requests
import urllib.parse

log = logging.getLogger(__name__)


def get_cognito_redirect_uri(request):
    return request.resource_url(request.site, 'staff', 'cognito-cb')


def login_redirect(request):
    """Redirect to the staff login page."""
    settings = request.ferlysettings
    qs = urllib.parse.urlencode([
        ('response_type', 'code'),
        ('client_id', settings.cognito_client_id),
        ('redirect_uri', get_cognito_redirect_uri(request)),
    ])

    url = 'https://%s/login?%s' % (settings.cognito_domain, qs)
    return HTTPSeeOther(url)


def resolve_staff_token(request, staff_token):
    """If a staff member is authenticated, get the StaffToken database row.

    If not, raise HTTPForbidden to redirect to staff login.

    Update cookies as necessary to help the user stay logged in.
    """
    if not staff_token:
        log.warning(
            "No staff_token received from %s, user_agent %s",
            request.remote_addr, repr(request.user_agent))
        raise HTTPForbidden()

    try:
        token_id_str, secret_str = staff_token.split('-', 1)
        token_id = int(token_id_str)
        secret = secret_str.encode('ascii')
    except Exception:
        log.exception(
            "Unable to parse staff_token cookie from %s", request.remote_addr)
        raise HTTPForbidden()

    st = request.dbsession.query(StaffToken).get(token_id)
    if st is None:
        log.warning(
            "No staff_token found with id=%s received from %s",
            token_id, request.remote_addr)
        raise HTTPForbidden()

    actual_sha256 = hashlib.sha256(secret).hexdigest()
    if not hmac.compare_digest(actual_sha256, st.secret_sha256):
        log.warning(
            "Hash mismatch on token %s from %s at %s",
            token_id, st.username, request.remote_addr)
        raise HTTPForbidden()

    now = datetime.datetime.utcnow()

    if now >= st.expires:
        log.info(
            "Token %s from %s at %s has expired",
            token_id, st.username, request.remote_addr)
        raise HTTPForbidden()

    if now < st.update_ts:
        # Trust this token until update_ts.
        log.debug(
            "Accepted token %s from %s at %s",
            token_id, st.username, request.remote_addr)
        return st

    # Re-verify the token using Amazon Cognito.

    tokens_encoded = Fernet(secret).decrypt(st.tokens_fernet.encode('ascii'))
    tokens = json.loads(tokens_encoded.decode('ascii'))
    access_token = tokens['access_token']
    settings = request.ferlysettings

    for attempt in (0, 1):
        info_url = 'https://%s/oauth2/userInfo' % settings.cognito_domain
        resp = requests.get(
            info_url, headers={
                'Authorization': 'Bearer %s' % access_token,
            })

        if (resp.status_code == 401 and
                attempt == 0 and
                'refresh_token' in tokens):
            # Try to refresh the token.
            log.warning(
                "Refreshing access token %s from %s at %s",
                token_id, st.username, request.remote_addr)
            tokens = refresh(request, tokens)
            access_token = tokens['access_token']
            tokens_encoded = json.dumps(tokens).encode('utf-8')
            tokens_fernet = Fernet(secret).encrypt(
                tokens_encoded).decode('ascii')
            st.tokens_fernet = tokens_fernet
            continue

        if 200 <= resp.status_code < 300:
            user_info = resp.json()
            break
        else:
            log.warning(
                "userInfo failed for token %s from %s at %s: %s",
                token_id, st.username, request.remote_addr, resp.content)
            raise HTTPForbidden()

    new_attrs = (
        ('user_agent', request.user_agent),
        ('remote_addr', request.remote_addr),
        ('username', user_info['username']),
        ('email', user_info['email']),
    )
    for attr, value in new_attrs:
        if getattr(st, attr) != value:
            setattr(st, attr, value)

    st.update_ts = now + datetime.timedelta(
        seconds=settings.token_trust_duration)
    st.expires = now + datetime.timedelta(seconds=settings.token_duration)

    log.info(
        "Updated staff user_info for token %s from %s at %s: %s",
        token_id, st.username, request.remote_addr, user_info)

    return st


def refresh(request, tokens):
    settings = request.ferlysettings
    token_url = 'https://%s/oauth2/token' % settings.cognito_domain
    token_data = [
        ('grant_type', 'refresh_token'),
        ('client_id', settings.cognito_client_id),
        ('refresh_token', tokens['refresh_token']),
    ]
    resp = requests.post(
        token_url,
        auth=(settings.cognito_client_id, settings.cognito_client_secret),
        data=token_data)
    resp.raise_for_status()
    return resp.json()
