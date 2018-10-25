from pyramid.decorator import reify
import os


class FerlySettings(object):

    def __init__(self, request):
        self._settings = request.registry.settings

    @reify
    def webpack_dist_dir(self):
        return self._settings['webpack_dist_dir']

    @reify
    def wingcash_api_url(self):
        return self._settings['wingcash_api_url']

    @reify
    def ferly_wc_id(self):
        return self._settings['ferly_wc_id']

    @reify
    def wingcash_client_id(self):
        res = os.environ.get('FERLY_WINGCASH_CLIENT_ID')
        if res:
            return res
        # return self._settings['keys']['client_id']
        return self._settings['client_id']

    @reify
    def wingcash_client_secret(self):
        res = os.environ.get('FERLY_WINGCASH_CLIENT_SECRET')
        if res:
            return res
        # return self._settings['keys']['client_secret']
        return self._settings['client_secret']

    @reify
    def ferly_token(self):
        # res = os.environ.get('FERLY_TOKEN')
        # if res:
        #     return res
        # return self._settings['keys']['ferly_token']
        # print('ferly_token:', self._settings['ferly_token'])
        return self._settings['ferly_token']
