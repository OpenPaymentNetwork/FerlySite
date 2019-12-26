
from pyramid.decorator import reify
from pyramid.settings import asbool
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
    def branch_api_url(self):
        return self._settings['branch_api_url']

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

    # No longer in use:
    # @reify
    # def wingcash_api_token(self):
    #     return os.environ.get('WINGCASH_API_TOKEN',
    #                           self._settings.get('wingcash_api_token'))

    @reify
    def distributor_uid(self):
        """The OPN UID of the cash distributor (a business)"""
        return self._settings['distributor_uid']

    @reify
    def distributor_manager_uid(self):
        """The OPN UID of the manager (an individual) of the distributor"""
        return self._settings['distributor_manager_uid']

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

    @reify
    def cognito_client_id(self):
        """Client ID for Amazon Cognito login"""
        return (
            os.environ.get('COGNITO_CLIENT_ID') or
            self._settings['cognito_client_id'])

    @reify
    def cognito_client_secret(self):
        """Client secret for Amazon Cognito login"""
        return (
            os.environ.get('COGNITO_CLIENT_SECRET') or
            self._settings['cognito_client_secret'])

    @reify
    def cognito_domain(self):
        """Domain of the Amazon Cognito service"""
        return self._settings['cognito_domain']

    @reify
    def cognito_region(self):
        """Region of the Amazon Cognito service"""
        return self._settings['cognito_region']

    @reify
    def cognito_userpool_id(self):
        """User pool ID of the Amazon Cognito service"""
        return self._settings['cognito_userpool_id']

    @reify
    def secure_cookie(self):
        """True if cookies should only be passed through HTTPS"""
        return asbool(self._settings.get('secure_cookie', True))

    @reify
    def token_trust_duration(self):
        """How long before checking and updating tokens, in seconds"""
        return int(self._settings.get('token_trust_duration', 60))

    @reify
    def token_duration(self):
        """How long until inactive tokens expire, in seconds"""
        return int(self._settings.get('token_duration', 15 * 60))

    @reify
    def token_delete_days(self):
        """How long to keep expired tokens, in days"""
        return int(self._settings.get('token_delete_days', 7))
