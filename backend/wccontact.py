from colander import Invalid
from pyramid.httpexceptions import HTTPServiceUnavailable
import logging
import os
import requests

log = logging.getLogger(__name__)


def wc_contact(
        request, method, urlTail, params={}, secret='',
        access_token=None, auth=False, return_errors=False, 
        anon=False, open_loop=False):
    """Issue an OPN API call and return the Response.

    The caller must specify which authentication mechanism to use:

    - anon (bool): If true, use no authentication.

    - auth (bool): Use Basic authentication to authenticate the app rather
      than an OPN profile.

    - secret (str): Provide a secret in the Authorization header.

    - access_token: Provide a Bearer access token in the Authorization header.

    Raise ValueError if no authentication mechanism is specified.

    If return_errors is true, return the Response even if OPN indicated
    a 4xx or 5xx error.
    """
    args = {}

    if method == 'POST':
        requests_func = requests.post
        args.update({'json': params})
    elif method == 'GET':
        requests_func = requests.get
        args.update({'params': params})
    else:
        raise Exception("Only 'GET' and 'POST' are accepted methods")

    if anon:
        # No authorization needed.
        pass
    elif auth:
        # Use HTTP Basic auth.
        if open_loop:
            wcauth = (
                request.ferlysettings.open_wingcash_client_id,
                request.ferlysettings.open_wingcash_client_secret)
        else:
            wcauth = (
                request.ferlysettings.wingcash_client_id,
                request.ferlysettings.wingcash_client_secret)
        args.update({'auth': wcauth})
    elif secret:
        # Use a secret value.
        authorization = 'wingcash secret="{0}"'.format(secret)
        args.update({'headers': {'Authorization': authorization}})
    elif access_token:
        # Use a Bearer access token.
        authorization = 'Bearer {0}'.format(access_token)
        args.update({'headers': {'Authorization': authorization}})
    else:
        # Note: we used to fall back on settings.wingcash_api_token,
        # but that setting was error prone. Now callers of wc_contact
        # are required to specify the authentication method.
        raise ValueError(
            "No authorization method was specified for wc_contact()")

    wingcash_api_url = request.ferlysettings.wingcash_api_url
    url = wingcash_api_url.strip('/') + "/" + urlTail.strip('/')
    response = requests_func(url, **args)
    try:
        response.raise_for_status()
    except Exception:
        log.error(
            "OPN responded to %s with %s: %s",
            url, response.status_code, response.text)
        try:
            error_json = response.json()
        except Exception:
            raise HTTPServiceUnavailable()
        else:
            if return_errors:
                return response
            else:
                if 'invalid' in error_json:
                    raise Invalid(None, msg=error_json['invalid'])
                else:
                    raise HTTPServiceUnavailable()
    else:
        return response

def b_contact(
        request, method, params={},
        return_errors=False):
    """Issue a branch API call and return the Response.

    If return_errors is true, return the Response even if Branch indicated
    a 4xx or 5xx error.
    """
    args = {}

    if method == 'POST':
        requests_func = requests.post
        args.update({'json': params})
    elif method == 'GET':
        requests_func = requests.get
        args.update({'params': params})
    else:
        raise Exception("Only 'GET' and 'POST' are accepted methods")

    url = request.ferlysettings.branch_api_url
    response = requests_func(url, **args)
    try:
        response.raise_for_status()
    except Exception:
        log.error(
            "Branch responded to %s with %s: %s",
            url, response.status_code, response.text)
        try:
            error_json = response.json()
        except Exception:
            raise HTTPServiceUnavailable()
        else:
            if return_errors:
                return response
            else:
                if 'invalid' in error_json:
                    raise Invalid(None, msg=error_json['invalid'])
                else:
                    raise HTTPServiceUnavailable()
    else:
        return response
