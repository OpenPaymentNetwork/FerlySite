from backend.appapi.schemas import recovery_views_schemas as schemas
from backend.testing import add_device
from backend.testing import DBFixture
from colander import Invalid
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class TestRecover(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.recovery_views import recover
        return recover(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'login': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params,headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.get_params = params = MagicMock()
        params.return_value = schemas.RecoverySchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.RecoverySchema))

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_wc_params(self, wc_contact):
        import uuid
        login = 'email@example.com'
        device_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, "defaultpassword0defaultpassword0"))
        request = self._make_request(login=login)
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'aa/signin-closed', auth=True, return_errors=True,
            params={'login': login, 'device_uuid': device_uuid})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_invalid_login_message(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'invalid': {'login': 'phone, email, or username'}}
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_usernames_rejected(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'completed_mfa': False,
            'factor_id': 'myfactor_id',
            'unauthenticated': {'username:myusername': 'info'}
        }
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_has_mfa(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True,
            'factor_id': 'myfactor_id',
        }
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_no_factor_id(self, wc_contact):
        wc_contact.return_value.json.return_value = {}
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_revealed_codes(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'factor_id': 'myfactor_id',
            'revealed_codes': 'mycodes',
            'unauthenticated': {'email:email@example.com': 'info'}
        }
        response = self._call(self._make_request())
        self.assertTrue('revealed_codes' in response)

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_response(self, wc_contact):
        good_values = {
            'secret': 'mysecret',
            'code_length': 9,
            'attempt_path': 'myattemptpath',
            'factor_id': 'myfactor_id',
        }
        bad_values = {
            'unauthenticated': {'email:email@example.com': 'info'},
            'bad_key': 'bad_val'
        }
        wc_contact.return_value.json.return_value = {
            **good_values, **bad_values}
        response = self._call(self._make_request())
        good_values.update({'login_type': 'email'})
        self.assertEqual(good_values, response)


class TestRecoverCode(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.recovery_views import recover_code
        return recover_code(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'code': '123456789',
            'secret': 'defaultsecret',
            'factor_id': 'defaultfactor_id',
            'attempt_path': 'default/attempt/path',
            'expo_token:': 'defaulttoken',
            'os': 'android'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
            })
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.RecoveryCodeSchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.RecoveryCodeSchema))

    def test_existing_device(self):
        add_device(self.dbsession)
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_wc_params(self, wc_contact):
        code = 'mycode'
        attempt_path = 'my/attempt/path'
        secret = 'mysecret'
        factor_id = 'myfactor_id'
        recaptcha_response = 'recaptcha'
        request = self._make_request(
            code=code, attempt_path=attempt_path, secret=secret,
            factor_id=factor_id, recaptcha_response=recaptcha_response)
        self._call(request)
        expected_url_tail = attempt_path + '/auth-uid'
        expected_wc_params = {
            'code': code,
            'factor_id': factor_id,
            'g-recaptcha-response': recaptcha_response
        }
        wc_contact.assert_called_with(
            request, 'POST', expected_url_tail, secret=secret,
            params=expected_wc_params, return_errors=True)

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_no_mfa(self, wc_contact):
        request = self._make_request()
        wc_contact.return_value.json.return_value = {
            'profile_id': 'myprofile_id'
        }
        wc_contact().status_code = 200
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_no_profile_id(self, wc_contact):
        request = self._make_request()
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True
        }
        wc_contact().status_code = 200
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})

    @patch('backend.appapi.views.recovery_views.wc_contact')
    def test_device_added(self, wc_contact):
        customer = add_device(self.dbsession)[0].customer
        os = 'android:28'
        expo_token = 'myexpo_token'
        request = self._make_request(
            os=os, expo_token=expo_token)
        request.headers = {
            'Authorization': 'Bearer newdevicenewdevicenewdevicenewdevice',
        }
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True,
            'profile_id': customer.wc_id,
        }
        wc_contact().status_code = 200
        self._call(request)
        from backend.database.models import Device
        devices = self.dbsession.query(Device).all()
        self.assertEqual(2, len(devices))
        # mock_device.assert_called_with(password=password,
        #                                customer_id=customer.id,
        #                                expo_token=expo_token, os=os)
        # request.dbsession.add.assert_called_with(mock_device.return_value)


class TestAddUid(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.recovery_views import add_uid
        return add_uid(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'uid_type': 'email',
            'login': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.get_params = params = MagicMock()
        params.return_value = schemas.AddUIDSchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_correct_schema_used(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.AddUIDSchema))

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_wc_params(self, get_device, wc_contact, get_wc_token):
        uid_type = 'email'
        login = 'defaultemail@example.com'
        request = self._make_request(uid_type=uid_type, login=login)
        get_wc_token.return_value = access_token = MagicMock()
        self._call(request)
        expected_params = {'login': login, 'uid_type': uid_type}
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/add-uid', params=expected_params,
            access_token=access_token)

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_revealed_codes(self, get_device, wc_contact, get_wc_token):
        wc_contact.return_value.json.return_value = {
            'revealed_codes': 'mycodes'
        }
        response = self._call(self._make_request())
        self.assertTrue('revealed_codes' in response)

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_response(self, get_device, wc_contact, get_wc_token):
        good_values = {
            'secret': 'mysecret',
            'code_length': 9,
            'attempt_id': 'myattemptid'
        }
        bad_values = {
            'bad_key': 'bad_val'
        }
        wc_contact.return_value.json.return_value = {
            **good_values, **bad_values}
        response = self._call(self._make_request())
        self.assertEqual(good_values, response)


class TestConfirmUid(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.recovery_views import confirm_uid
        return confirm_uid(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'code': 'defaultcode',
            'secret': 'defaultsecret',
            'attempt_id': 'defaultattemptid'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.get_params = params = MagicMock()
        params.return_value = schemas.AddUIDCodeSchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_correct_schema_used(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.AddUIDCodeSchema))

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_with_replace_uid(self, get_device, wc_contact, get_wc_token):
        replace_uid = 'oldemail@example.com'
        self._call(self._make_request(replace_uid=replace_uid))
        self.assertEqual(
            wc_contact.call_args[1]['params'].get('replace_uid'), replace_uid)

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_wc_params(self, get_device, wc_contact, get_wc_token):
        params = {
            'secret': 'mysecret',
            'attempt_id': 'myattemptid',
            'code': 'mycode',
        }
        captcha_response = 'captcha'
        wc_params = {**params, 'g-recaptcha-response': captcha_response}
        call_params = {**params, 'recaptcha_response': captcha_response}
        request = self._make_request(**call_params)
        get_wc_token.return_value = access_token = MagicMock()
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/add-uid-confirm', params=wc_params,
            access_token=access_token, return_errors=True)

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_wc_invalid(self, get_device, wc_contact, get_wc_token):
        wc_contact().json.return_value = {'invalid': {'code': 'wrong code'}}
        wc_contact().status_code = 400
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.appapi.views.recovery_views.get_wc_token')
    @patch('backend.appapi.views.recovery_views.wc_contact')
    @patch('backend.appapi.views.recovery_views.get_device')
    def test_recaptcha_required(self, get_device, wc_contact, get_wc_token):
        wc_contact().json.return_value = {'error': 'recaptcha_required'}
        wc_contact().status_code = 410
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'code_expired'})

class TestLogin(TestCase):
    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.recovery_views import login
        return login(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'profile_id': 'defaultcode',
            'expo_token': 'my_expo_token',
            'os': 'nt'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params,headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.LoginSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.LoginSchema))
    
    def test_existing_device(self):
        add_device(self.dbsession)
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected_auth_attempt'})
