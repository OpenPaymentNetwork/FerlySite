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
        res = os.environ.get('FERLY_TOKEN')
        if res:
            return res
        return self._settings['ferly_token']

    @reify
    def sendgrid_api_key(self):
        return os.environ.get('SENDGRID_API_KEY')

    @reify
    def twilio_sid(self):
        return os.environ.get('TWILIO_SID', self._settings.get('twilio_sid'))

    @reify
    def twilio_auth_token(self):
        return os.environ.get(
            'TWILIO_AUTH_TOKEN', self._settings.get('twilio_auth_token'))

    @reify
    def twilio_from(self):
        return os.environ.get('TWILIO_FROM', self._settings.get('twilio_from'))

    @reify
    def aws_access_key_id(self):
        return os.environ.get('AWS_ACCESS_KEY_ID')

    @reify
    def aws_secret_key(self):
        return os.environ.get('AWS_SECRET_KEY')
