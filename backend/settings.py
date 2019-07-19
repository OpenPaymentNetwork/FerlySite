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
    def wingcash_profile_id(self):
        return self._settings['wingcash_profile_id']

    @reify
    def wingcash_client_id(self):
        return os.environ.get('WINGCASH_CLIENT_ID',
                              self._settings.get('wingcash_client_id'))

    @reify
    def wingcash_client_secret(self):
        return os.environ.get('WINGCASH_CLIENT_SECRET',
                              self._settings.get('wingcash_client_secret'))

    @reify
    def wingcash_api_token(self):
        return os.environ.get('WINGCASH_API_TOKEN',
                              self._settings.get('wingcash_api_token'))

    @reify
    def sendgrid_api_key(self):
        return os.environ.get('SENDGRID_API_KEY')

    @reify
    def twilio_sid(self):
        return os.environ.get('TWILIO_SID', self._settings.get('twilio_sid'))

    @reify
    def twilio_auth_token(self):
        return os.environ.get('TWILIO_AUTH_TOKEN',
                              self._settings.get('twilio_auth_token'))

    @reify
    def twilio_from(self):
        return os.environ.get('TWILIO_FROM', self._settings.get('twilio_from'))

    @reify
    def aws_access_key_id(self):
        return os.environ.get('AWS_ACCESS_KEY_ID')

    @reify
    def aws_secret_key(self):
        return os.environ.get('AWS_SECRET_KEY')

    @reify
    def stripe_api_key(self):
        return os.environ.get('STRIPE_API_KEY',
                              self._settings.get('stripe_api_key'))

    @reify
    def environment(self):
        return self._settings.get('env_file').split('.')[0]

    @reify
    def usps_username(self):
        return os.environ.get('USPS_USERNAME')

    @reify
    def usps_address_info_url(self):
        return self._settings['usps_address_info_url']
