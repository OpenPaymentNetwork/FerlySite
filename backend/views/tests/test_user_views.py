from backend.models.models import Device
from backend.views.userviews import edit_profile
from backend.views.userviews import is_user
from backend.views.userviews import signup
from backend.views.userviews import wallet
from backend.views.userviews import add_uid
from backend.views.userviews import confirm_uid
from backend.views.userviews import recover
from backend.views.userviews import recover_code
from colander import Invalid
from unittest import TestCase
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestRecover(TestCase):

    def _call(self, *args, **kw):
        return recover(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'login': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    @patch('backend.views.userviews.wc_contact')
    def test_wc_params(self, wc_contact):
        login = 'email@example.com'
        device_id = 'mydeviceid'
        request = self._make_request(login=login, device_id=device_id)
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'aa/signin-closed', auth=True, returnErrors=True,
            params={'login': login, 'device_uuid': device_id})

    @patch('backend.views.userviews.wc_contact')
    def test_invalid_login_message(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'invalid': {'login': 'phone, email, or username'}}
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.views.userviews.wc_contact')
    def test_usernames_rejected(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'completed_mfa': False,
            'factor_id': 'myfactor_id',
            'unauthenticated': {'username:myusername': 'info'}
        }
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.views.userviews.wc_contact')
    def test_has_mfa(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True,
            'factor_id': 'myfactor_id',
        }
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'unexpected auth attempt'})

    @patch('backend.views.userviews.wc_contact')
    def test_no_factor_id(self, wc_contact):
        wc_contact.return_value.json.return_value = {}
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'unexpected auth attempt'})

    @patch('backend.views.userviews.wc_contact')
    def test_revealed_codes(self, wc_contact):
        wc_contact.return_value.json.return_value = {
            'factor_id': 'myfactor_id',
            'revealed_codes': 'mycodes',
            'unauthenticated': {'email:email@example.com': 'info'}
        }
        response = self._call(self._make_request())
        self.assertTrue('revealed_codes' in response)

    @patch('backend.views.userviews.wc_contact')
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

    def _call(self, *args, **kw):
        return recover_code(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'code': '123456789',
            'secret': 'defaultsecret',
            'factor_id': 'defaultfactor_id',
            'attempt_path': 'default/attempt/path'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_code_required(self):
        with self.assertRaisesRegex(Invalid, "'code': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_secret_required(self):
        with self.assertRaisesRegex(Invalid, "'secret': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_factor_id_required(self):
        with self.assertRaisesRegex(Invalid, "'factor_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_attempt_path_required(self):
        with self.assertRaisesRegex(Invalid, "'attempt_path': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_existing_device(self):
        request = self._make_request()
        query = request.dbsession.query.return_value
        query.filter.return_value.first.return_value = 'existing_device'
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected auth attempt'})

    @patch('backend.views.userviews.wc_contact')
    def test_wc_params(self, wc_contact):
        code = 'mycode'
        attempt_path = 'my/attempt/path'
        secret = 'mysecret'
        factor_id = 'myfactor_id'
        request = self._make_request(code=code, attempt_path=attempt_path,
                                     secret=secret, factor_id=factor_id)
        query = request.dbsession.query.return_value
        query.filter.return_value.first.return_value = None
        self._call(request)
        expected_url_tail = attempt_path + '/auth-uid'
        expected_wc_params = {'code': code, 'factor_id': factor_id}
        wc_contact.assert_called_with(request, 'POST', expected_url_tail,
                                      secret=secret, params=expected_wc_params)

    @patch('backend.views.userviews.wc_contact')
    def test_no_mfa(self, wc_contact):
        request = self._make_request()
        query = request.dbsession.query.return_value
        query.filter.return_value.first.return_value = None
        wc_contact.return_value.json.return_value = {
            'profile_id': 'myprofile_id'
        }
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected auth attempt'})

    @patch('backend.views.userviews.wc_contact')
    def test_no_profile_id(self, wc_contact):
        request = self._make_request()
        query = request.dbsession.query.return_value
        query.filter.return_value.first.return_value = None
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True
        }
        response = self._call(request)
        self.assertEqual(response, {'error': 'unexpected auth attempt'})

    @patch('backend.views.userviews.Device')
    @patch('backend.views.userviews.wc_contact')
    def test_device_added(self, wc_contact, mock_device):
        device_id = 'mydevice_id'
        request = self._make_request(device_id=device_id)
        query = request.dbsession.query.return_value
        query.filter.return_value.first.return_value = None
        profile_id = 'myprofile_id'
        wc_contact.return_value.json.return_value = {
            'completed_mfa': True,
            'profile_id': profile_id
        }
        query.filter.return_value.one.return_value = user = MagicMock()
        user.id = 'myuserid'
        self._call(request)
        mock_device.assert_called_with(device_id=device_id, user_id=user.id)
        request.dbsession.add.assert_called_with(mock_device.return_value)


class TestAddUid(TestCase):

    def _call(self, *args, **kw):
        return add_uid(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'uid_type': 'email',
            'login': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_uid_type_required(self):
        with self.assertRaisesRegex(Invalid, "'uid_type': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_invalid_uid_type(self):
        bad_uid_type = 'username'
        request = self._make_request(uid_type=bad_uid_type)
        error = "'uid_type': '\"{0}\" is not one of phone, email'".format(
            bad_uid_type)
        with self.assertRaisesRegex(Invalid, error):
            self._call(request)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_wc_params(self, wc_contact, get_wc_token):
        uid_type = 'email'
        login = 'defaultemail@example.com'
        request = self._make_request(uid_type=uid_type, login=login)
        get_wc_token.return_value = access_token = MagicMock()
        self._call(request)
        expected_params = {'login': login, 'uid_type': uid_type}
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/add-uid', params=expected_params,
            access_token=access_token)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_revealed_codes(self, wc_contact, get_wc_token):
        wc_contact.return_value.json.return_value = {
            'revealed_codes': 'mycodes'
        }
        response = self._call(self._make_request())
        self.assertTrue('revealed_codes' in response)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_response(self, wc_contact, get_wc_token):
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
        return confirm_uid(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'code': 'defaultcode',
            'secret': 'defaultsecret',
            'attempt_id': 'defaultattemptid'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_code_required(self):
        with self.assertRaisesRegex(Invalid, "'code': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_secret_required(self):
        with self.assertRaisesRegex(Invalid, "'secret': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_attempt_id_required(self):
        with self.assertRaisesRegex(Invalid, "'attempt_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_with_replace_uid(self, wc_contact, get_wc_token):
        replace_uid = 'oldemail@example.com'
        self._call(self._make_request(replace_uid=replace_uid))
        self.assertEqual(
            wc_contact.call_args[1]['params'].get('replace_uid'), replace_uid)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_wc_params(self, wc_contact, get_wc_token):
        wc_params = {
            'secret': 'mysecret',
            'attempt_id': 'myattemptid',
            'code': 'mycode'
        }
        request = self._make_request(**wc_params)
        get_wc_token.return_value = access_token = MagicMock()
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/add-uid-confirm', params=wc_params,
            access_token=access_token, returnErrors=True)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_wc_invalid(self, wc_contact, get_wc_token):
        wc_contact().json.return_value = {'invalid': {'code': 'wrong code'}}
        wc_contact().status_code = 400
        with self.assertRaises(Invalid):
            self._call(self._make_request())

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    def test_recaptcha_required(self, wc_contact, get_wc_token):
        wc_contact().json.return_value = {'error': 'recaptcha_required'}
        wc_contact().status_code = 400
        response = self._call(self._make_request())
        self.assertEqual(response, {
            'error': 'bad_attempt',
            'error_description': 'Attempt denied, retry with new code.'
        })


class TestWallet(TestCase):

    def _call(self, *args, **kw):
        return wallet(*args, **kw)

    def test_no_params(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {'device_id': 'Required'}
        self.assertEqual(expected_response, e.asdict())


class TestSignUp(TestCase):

    def _call(self, *args, **kw):
        return signup(*args, **kw)

    def test_no_params(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {
            'device_id': 'Required',
            'first_name': 'Required',
            'username': 'Required',
            'last_name': 'Required'
        }
        self.assertEqual(expected_response, e.asdict())

    def test_already_registered(self):
        request_params = {
            'device_id': 'deviceid',
            'first_name': 'firstname',
            'last_name': 'lastname',
            'username': 'username'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mdevice = MagicMock()
        mock_query.filter.return_value.first.return_value = mdevice
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_query(self):
        device_id = '123'
        request_params = {
            'device_id': device_id,
            'first_name': 'firstname',
            'last_name': 'lastname',
            'username': 'username',
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.Device')
    @patch('backend.views.userviews.User')
    @patch('backend.views.userviews.wc_contact')
    def test_add_user(self, mock_wc_contact, mock_user, mock_device):
        first_name = 'firstname'
        last_name = 'lastname'
        username = 'username'
        request_params = {
            'device_id': 'deviceid',
            'first_name': first_name,
            'last_name': last_name,
            'username': username
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name, 'username': username,
                'last_name': last_name, 'expo_token': ''}
        self._call(request)
        mock_user.assert_called_once_with(**user)
        mdbsession.add.assert_any_call(mock_user.return_value)

    @patch('backend.views.userviews.Device')
    @patch('backend.views.userviews.User')
    @patch('backend.views.userviews.wc_contact')
    def test_save_expo_token(self, mock_wc_contact, mock_user, mock_device):
        first_name = 'firstname'
        last_name = 'lastname'
        username = 'username'
        token = 'token'
        request_params = {
            'device_id': 'deviceid',
            'first_name': first_name,
            'last_name': last_name,
            'expo_token': token,
            'username': username
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name, 'username': username,
                'last_name': last_name, 'expo_token': token}
        self._call(request)
        mock_user.assert_called_once_with(**user)

    @patch('backend.views.userviews.Device')
    @patch('backend.views.userviews.User')
    @patch('backend.views.userviews.wc_contact')
    def test_add_device(self, mock_wc_contact, mock_user, mock_device):
        device_id = 'deviceid'
        request_params = {
            'device_id': device_id,
            'first_name': 'firstname',
            'last_name': 'lastname',
            'username': 'username'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mock_user.return_value.id = user_id = 'userid'
        device = {'device_id': device_id, 'user_id': user_id}
        self._call(request)
        mock_device.assert_called_once_with(**device)
        mdbsession.add.assert_any_call(mock_device.return_value)

    @patch('backend.views.userviews.Device')
    @patch('backend.views.userviews.User')
    @patch('backend.views.userviews.wc_contact')
    def test_db_flush(self, mock_wc_contact, mock_user, mock_device):
        request_params = {
            'device_id': 'deviceid',
            'first_name': 'firstname',
            'last_name': 'lastname',
            'username': 'username'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mdevice = mock_device.return_value
        muser = mock_user.return_value
        self._call(request)
        mdbsession.assert_has_calls(
            [call.add(muser), call.flush, call.add(mdevice)])

    @patch('backend.views.userviews.wc_contact')
    def test_wc_contact_params(self, mock_wc_contact):
        first_name = 'firstname'
        last_name = 'lastname'
        request_params = {
            'device_id': 'deviceid',
            'first_name': first_name,
            'last_name': last_name,
            'username': 'username'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        self._call(request)
        args = (request, 'POST', 'p/add-individual')
        params = {
            'first_name': first_name,
            'last_name': last_name,
            'agreed_terms_and_privacy': True
        }
        kw = {
            'params': params,
            'auth': True
        }
        mock_wc_contact.assert_called_once_with(*args, **kw)

    def test_deny_existing_username(self):
        request = pyramid.testing.DummyRequest(params={
            'first_name': 'firstname',
            'last_name': 'lastname',
            'username': 'username',
            'device_id': 'deviceid'
        })
        mdbsession = request.dbsession = MagicMock()
        mock_query_filter = mdbsession.query.return_value.filter.return_value
        mock_query_filter.first.side_effect = [None, not None]
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})


class TestEditProfile(TestCase):

    def _call(self, *args, **kw):
        return edit_profile(*args, **kw)

    def test_username_required(self):
        request = pyramid.testing.DummyRequest(params={})
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
            self._call(request)

    def test_first_name_required(self):
        request = pyramid.testing.DummyRequest(params={})
        with self.assertRaisesRegex(Invalid, "'first_name': 'Required'"):
            self._call(request)

    def test_last_name_required(self):
        request = pyramid.testing.DummyRequest(params={})
        with self.assertRaisesRegex(Invalid, "'last_name': 'Required'"):
            self._call(request)

    def test_device_id_required(self):
        request = pyramid.testing.DummyRequest(params={})
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(request)

    def test_username_4_characters(self):
        request = pyramid.testing.DummyRequest(params={
            'username': 'abc'
        })
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must contain at least 4 characters'"):
            self._call(request)

    def test_username_not_21_characters(self):
        request = pyramid.testing.DummyRequest(params={
            'username': 'abcdefghijklmnopqrstu'
        })
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must not be longer than 20 characters'"):
            self._call(request)

    def test_username_starts_with_letter(self):
        request = pyramid.testing.DummyRequest(params={
            'username': '1234'
        })
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must not start with a number'"):
            self._call(request)

    def test_invalid_username(self):
        request = pyramid.testing.DummyRequest(params={
            'username': 'abc!'
        })
        with self.assertRaisesRegex(
                Invalid,
                ("'username': "
                 "'Can only contain letters, numbers, and periods'")):
            self._call(request)

    @patch('backend.views.userviews.wc_contact')
    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.get_device')
    @patch('backend.schema.EditProfileSchema')
    def test_unchanged_username(
            self, schema, get_device, get_token, wc_contact):
        request = pyramid.testing.DummyRequest()
        request.dbsession = mdbsession = MagicMock()
        mock_user = get_device.return_value.user
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = mock_user
        response = self._call(request)
        self.assertEqual(response, {})

    @patch('backend.views.userviews.get_device')
    @patch('backend.schema.EditProfileSchema')
    def test_existing_username(self, schema, get_device):
        request = pyramid.testing.DummyRequest()
        request.dbsession = mdbsession = MagicMock()
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = not None
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    @patch('backend.views.userviews.get_device')
    def test_edit_username_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = current_first_name = 'firstname'
        mock_user.last_name = current_last_name = 'lastname'
        mock_user.username = 'current_username'
        newusername = 'newusername'
        request = pyramid.testing.DummyRequest(params={
            'first_name': current_first_name,
            'last_name': current_last_name,
            'username': newusername,
            'device_id': 'deviceid'
        })
        request.dbsession = mdbsession = MagicMock()
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        self.assertFalse(get_wc_token.called)
        self.assertFalse(wc_contact.called)
        self.assertEqual(mock_user.first_name, current_first_name)
        self.assertEqual(mock_user.last_name, current_last_name)
        self.assertEqual(mock_user.username, newusername)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    @patch('backend.views.userviews.get_device')
    def test_edit_first_name_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = 'firstname'
        mock_user.last_name = current_last_name = 'lastname'
        mock_user.username = current_username = 'username'
        new_first_name = 'new_first_name'
        request = pyramid.testing.DummyRequest(params={
            'first_name': new_first_name,
            'last_name': current_last_name,
            'username': current_username,
            'device_id': 'deviceid'
        })
        request.dbsession = mdbsession = MagicMock()
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, mock_user)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': new_first_name,
                'last_name': current_last_name
            })
        self.assertEqual(mock_user.first_name, new_first_name)
        self.assertEqual(mock_user.last_name, current_last_name)
        self.assertEqual(mock_user.username, current_username)

    @patch('backend.views.userviews.get_wc_token')
    @patch('backend.views.userviews.wc_contact')
    @patch('backend.views.userviews.get_device')
    def test_edit_last_name_only(self, get_device, wc_contact, get_wc_token):
        mock_user = get_device.return_value.user
        mock_user.first_name = current_first_name = 'firstname'
        mock_user.last_name = 'lastname'
        mock_user.username = current_username = 'username'
        new_last_name = 'new_first_name'
        request = pyramid.testing.DummyRequest(params={
            'first_name': current_first_name,
            'last_name': new_last_name,
            'username': current_username,
            'device_id': 'deviceid'
        })
        request.dbsession = mdbsession = MagicMock()
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, mock_user)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': current_first_name,
                'last_name': new_last_name
            })
        self.assertEqual(mock_user.first_name, current_first_name)
        self.assertEqual(mock_user.last_name, new_last_name)
        self.assertEqual(mock_user.username, current_username)


class TestIsUser(TestCase):

    def _call(self, *args, **kw):
        return is_user(*args, **kw)

    def test_no_params(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {'device_id': 'Required'}
        self.assertEqual(expected_response, e.asdict())

    def test_invalid_device_id(self):
        request_params = {
            'device_id': 'asdf'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        response = self._call(request)
        self.assertFalse(response.get('is_user'))

    def test_valid_device_id(self):
        request_params = {
            'device_id': 'asdf'
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_device = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_device
        response = self._call(request)
        self.assertTrue(response.get('is_user'))

    def test_query(self):
        device_id = '123'
        request_params = {
            'device_id': device_id
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mdevice = MagicMock()
        mock_query = mdbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        mock_filter.return_value.first.return_value = mdevice
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))
