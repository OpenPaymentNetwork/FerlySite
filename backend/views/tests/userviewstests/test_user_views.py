from backend.models.models import Device
from backend.views.userviews.userviews import edit_profile
from backend.views.userviews.userviews import is_user
from backend.views.userviews.userviews import signup
from backend.views.userviews.userviews import wallet
from colander import Invalid
from unittest import TestCase
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


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

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername',
            'expo_token:': 'defaulttoken',
            'os': 'defaultos:android'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_first_name_required(self):
        with self.assertRaisesRegex(Invalid, "'first_name': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_last_name_required(self):
        with self.assertRaisesRegex(Invalid, "'last_name': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_username_required(self):
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_os_required(self):
        with self.assertRaisesRegex(Invalid, "'os': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_already_registered(self):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mdevice = MagicMock()
        mock_query.filter.return_value.first.return_value = mdevice
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_query(self):
        device_id = '123'
        request = self._make_request(device_id=device_id)
        mock_query = request.dbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_add_user(self, mock_wc_contact, mock_user, mock_device):
        first_name = 'firstname'
        last_name = 'lastname'
        username = 'username'
        request = self._make_request(
            first_name=first_name, last_name=last_name, username=username)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name, 'username': username,
                'last_name': last_name}
        self._call(request)
        mock_user.assert_called_once_with(**user)
        request.dbsession.add.assert_any_call(mock_user.return_value)

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_add_device(self, mock_wc_contact, mock_user, mock_device):
        device_id = 'deviceid'
        os = 'android:28'
        expo_token = 'myexpotoken'
        request = self._make_request(
            device_id=device_id, os=os, expo_token=expo_token)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mock_user.return_value.id = user_id = 'userid'
        device = {'device_id': device_id, 'user_id': user_id, 'os': os,
                  'expo_token': expo_token}
        self._call(request)
        mock_device.assert_called_once_with(**device)
        request.dbsession.add.assert_any_call(mock_device.return_value)

    @patch('backend.views.userviews.userviews.Device')
    @patch('backend.views.userviews.userviews.User')
    @patch('backend.views.userviews.userviews.wc_contact')
    def test_db_flush(self, mock_wc_contact, mock_user, mock_device):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mdevice = mock_device.return_value
        muser = mock_user.return_value
        self._call(request)
        request.dbsession.assert_has_calls(
            [call.add(muser), call.flush, call.add(mdevice)])

    @patch('backend.views.userviews.userviews.wc_contact')
    def test_wc_contact_params(self, mock_wc_contact):
        first_name = 'firstname'
        last_name = 'lastname'
        request = self._make_request(
            first_name=first_name, last_name=last_name)
        mock_query = request.dbsession.query.return_value
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
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.side_effect = [None, not None]
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

    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.get_device')
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

    @patch('backend.views.userviews.userviews.get_device')
    @patch('backend.schema.EditProfileSchema')
    def test_existing_username(self, schema, get_device):
        request = pyramid.testing.DummyRequest()
        request.dbsession = mdbsession = MagicMock()
        mock_filter = mdbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = not None
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
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

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
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

    @patch('backend.views.userviews.userviews.get_wc_token')
    @patch('backend.views.userviews.userviews.wc_contact')
    @patch('backend.views.userviews.userviews.get_device')
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
