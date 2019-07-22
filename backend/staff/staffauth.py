
from backend.database.models import StaffToken
from cryptography.fernet import Fernet
from pyramid.decorator import reify
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


def resolve_token(request, params=None, field='staff_token'):
    resolver = TokenResolver(request, params, field)
    return resolver()


class TokenResolver:
    """Authenticate the user with a token."""
    def __init__(self, request, params=None, field='staff_token'):
        self.request = request
        if params is not None:
            self.token_input = params.get(field)
        else:
            self.token_input = request.cookies.get(field)

    def __call__(self):
        """If the user has an authenticated token, get the token row.

        If not, raise HTTPForbidden (which should redirect to login).

        Update cookies as necessary to help the user stay logged in.
        """
        token_row = self.authenticated_token_row

        if self.now < token_row.update_ts:
            # Trust this token until update_ts.
            log.debug(
                "Trusting token %s from %s at %s",
                token_row.id, token_row.username, self.request.remote_addr)
            return token_row

        self.sync_token(token_row)
        return token_row

    def forbidden(self):
        error = HTTPForbidden()
        error.staff_token_required = True
        raise error

    @reify
    def now(self):
        return datetime.datetime.utcnow()

    @reify
    def decoded_token(self):
        """Return (token_id: int, secret: bytes).

        Raise HTTPForbidden if the token is missing or unparseable.
        """
        request = self.request
        token_input = self.token_input

        if not token_input:
            log.warning(
                "No token received from %s, user_agent %s",
                request.remote_addr, repr(request.user_agent))
            raise self.forbidden()

        try:
            token_id_str, secret_str = token_input.split('-', 1)
            token_id = int(token_id_str)
            secret = secret_str.encode('ascii')
        except Exception:
            log.exception(
                "Unable to parse token from %s", request.remote_addr)
            raise self.forbidden()

        return token_id, secret

    @reify
    def authenticated_token_row(self):
        """Return the authenticated StaffTokenRow."""
        request = self.request
        token_id, secret = self.decoded_token

        token_row = request.dbsession.query(StaffToken).get(token_id)
        if token_row is None:
            log.warning(
                "No token found with id=%s received from %s",
                token_id, request.remote_addr)
            raise self.forbidden()

        actual_sha256 = hashlib.sha256(secret).hexdigest()
        if not hmac.compare_digest(actual_sha256, token_row.secret_sha256):
            log.warning(
                "Hash mismatch on token %s from %s at %s",
                token_id, token_row.username, request.remote_addr)
            raise self.forbidden()

        now = self.now

        if now >= token_row.expires:
            log.info(
                "Token %s from %s at %s has expired",
                token_id, token_row.username, request.remote_addr)
            raise self.forbidden()

        return token_row

    def sync_token(self, token_row):
        """Sync with the Amazon Cognito record.

        Raise HTTPForbidden if the token is no longer valid.
        """
        request = self.request
        token_id, secret = self.decoded_token
        tokens_encoded = Fernet(secret).decrypt(
            token_row.tokens_fernet.encode('ascii'))
        tokens_json = json.loads(tokens_encoded.decode('ascii'))
        print(tokens_json)
        access_token = tokens_json['access_token']
        settings = request.ferlysettings

        for attempt in (0, 1):
            info_url = 'https://%s/oauth2/userInfo' % settings.cognito_domain
            resp = requests.get(
                info_url, headers={
                    'Authorization': 'Bearer %s' % access_token,
                })

            if (resp.status_code == 401 and
                    attempt == 0 and
                    'refresh_token' in tokens_json):
                # Try to refresh the token.
                log.warning(
                    "Refreshing access token %s from %s at %s",
                    token_id, token_row.username, request.remote_addr)
                tokens_json = self.refresh(tokens_json)
                access_token = tokens_json['access_token']
                tokens_encoded = json.dumps(tokens_json).encode('utf-8')
                tokens_fernet = Fernet(secret).encrypt(
                    tokens_encoded).decode('ascii')
                token_row.tokens_fernet = tokens_fernet
                continue

            if 200 <= resp.status_code < 300:
                user_info = resp.json()
                break
            else:
                log.warning(
                    "userInfo failed for token %s from %s at %s: %s",
                    token_id, token_row.username, request.remote_addr,
                    resp.content)
                raise self.forbidden()

        new_attrs = (
            ('user_agent', request.user_agent),
            ('remote_addr', request.remote_addr),
            ('username', user_info['username']),
            ('email', user_info['email']),
        )
        for attr, value in new_attrs:
            if getattr(token_row, attr) != value:
                setattr(token_row, attr, value)

        token_row.update_ts = self.now + datetime.timedelta(
            seconds=settings.token_trust_duration)
        token_row.expires = self.now + datetime.timedelta(
            seconds=settings.token_duration)

        log.info(
            "Updated user_info for token %s from %s at %s: %s",
            token_id, token_row.username, request.remote_addr, user_info)

    def refresh(self, tokens_json):
        """Given an old tokens_json, try to refresh the tokens"""
        settings = self.request.ferlysettings
        token_url = 'https://%s/oauth2/token' % settings.cognito_domain
        token_data = [
            ('grant_type', 'refresh_token'),
            ('client_id', settings.cognito_client_id),
            ('refresh_token', tokens_json['refresh_token']),
        ]
        resp = requests.post(
            token_url,
            auth=(settings.cognito_client_id, settings.cognito_client_secret),
            data=token_data)
        try:
            resp.raise_for_status()
        except Exception as e:
            token_row = self.authenticated_token_row
            log.error(
                "Unable to refresh token %s from %s at %s: %s",
                token_row.id, token_row.username, self.request.remote_addr, e)
            raise self.forbidden()
        return resp.json()
