from colander import Invalid
from pyramid.httpexceptions import HTTPServiceUnavailable
import os
import requests


def wc_contact(request, method, urlTail, params={},
               access_token=None, auth=False):
    args = {}

    if method == 'POST':
        requests_func = requests.post
        args.update({'data': params})
    elif method == 'GET':
        requests_func = requests.get
        args.update({'params': params})
    else:
        raise Exception("Only 'GET' and 'POST' are accepted methods")

    if auth:
        wcauth = (  # TODO Use devkeys for these, not the ini file
            request.ferlysettings.wingcash_client_id,
            request.ferlysettings.wingcash_client_secret)
        args.update({'auth': wcauth})
    else:
        token = access_token or request.ferlysettings.ferly_token
        args.update({'headers': {'Authorization': 'Bearer ' + token}})

    wingcash_api_url = request.ferlysettings.wingcash_api_url
    url = os.path.join(wingcash_api_url, urlTail.strip('/'))
    try:
        response = requests_func(url, **args)
        response.raise_for_status()
    except Exception:
        try:
            error_json = response.json()
        except Exception:
            raise HTTPServiceUnavailable
        else:
            # return false and raise invalid in userview?
            if 'invalid' in error_json:
                raise Invalid(None, msg=error_json['invalid'])
            else:
                # wc ise, or bad token request.
                raise HTTPServiceUnavailable
    else:
        return response


def get_wc_token(request, user):
    # check memcached

    params = {
        'uid': 'wingcash:' + user.wc_id,
    }

    response = wc_contact(request, 'GET', 'p/token', params, auth=True)
    access_token = response.json().get('access_token')

    # store in memcached

    return access_token
