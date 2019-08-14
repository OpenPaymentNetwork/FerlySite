from colander import Invalid
from pyramid.httpexceptions import HTTPServiceUnavailable
import logging
import os
import requests

log = logging.getLogger(__name__)


def wc_contact(
        request, method, urlTail, params={}, secret='',
        access_token=None, auth=False, return_errors=False):
    args = {}

    if method == 'POST':
        requests_func = requests.post
        args.update({'data': params})
    elif method == 'GET':
        requests_func = requests.get
        args.update({'json': params})
    else:
        raise Exception("Only 'GET' and 'POST' are accepted methods")

    if auth:
        wcauth = (
            request.ferlysettings.wingcash_client_id,
            request.ferlysettings.wingcash_client_secret)
        args.update({'auth': wcauth})
    else:
        if secret:
            authorization = 'wingcash secret="{0}"'.format(secret)
        else:
            token = access_token or request.ferlysettings.wingcash_api_token
            authorization = 'Bearer {0}'.format(token)
        args.update({'headers': {'Authorization': authorization}})

    wingcash_api_url = request.ferlysettings.wingcash_api_url
    url = os.path.join(wingcash_api_url, urlTail.strip('/'))
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
