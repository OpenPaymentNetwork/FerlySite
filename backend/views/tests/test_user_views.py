from backend.models.models import Device
from backend.views.userviews import is_user
from backend.views.userviews import signup
from backend.views.userviews import wallet
from colander import Invalid
from pyramid import testing as pyramidtesting
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch


class TestWallet(TestCase):

    def _call(self, *args, **kw):
        return wallet(*args, **kw)

    def test_no_params(self):
        request = pyramidtesting.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {'device_id': 'Required'}
        self.assertEqual(expected_response, e.asdict())

    # test invalid device id? -no, just that get device is called
    # test calls get_wc_token and and wc_contact params (one test?)
    # test properly handles designs not in db ? - should n't show up,

    # assert handles design from wc thats not in our db
    # assert handles bad wc response, but 200
        # (4xx and 5xx raise exceptions in wc_contact)


class TestSignUp(TestCase):

    def _call(self, *args, **kw):
        return signup(*args, **kw)

    def test_no_params(self):
        request = pyramidtesting.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {
            'device_id': 'Required',
            'first_name': 'Required',
            'last_name': 'Required'
        }
        self.assertEqual(expected_response, e.asdict())

    def test_already_registered(self):
        request_params = {
            'device_id': 'deviceid',
            'first_name': 'firstname',
            'last_name': 'lastname'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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
            'last_name': 'lastname'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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
        request_params = {
            'device_id': 'deviceid',
            'first_name': first_name,
            'last_name': last_name
        }
        request = pyramidtesting.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name,
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
        token = 'token'
        request_params = {
            'device_id': 'deviceid',
            'first_name': first_name,
            'last_name': last_name,
            'expo_token': token
        }
        request = pyramidtesting.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        mock_user.return_value.id = 'userid'
        user = {'wc_id': wc_id, 'first_name': first_name,
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
            'last_name': 'lastname'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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
            'last_name': 'lastname'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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
            'last_name': last_name
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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

    # TODO test wc_contact fails


# class TestPurchase(TestCase):

#     def _call(self, *args, **kw):
#         return purchase(*args, **kw)

#     def test_no_params(self):
#         request = pyramidtesting.DummyRequest()
#         with self.assertRaises(Invalid) as cm:
#             self._call(request)
#         e = cm.exception
#         expected_response = {
#             'device_id': 'Required',
#             'design_id': 'Required',
#             'amount': 'Required'
#         }
#         self.assertEqual(expected_response, e.asdict())

#     @patch('backend.views.userviews.wc_contact')
#     @patch('backend.views.userviews.get_device')
#     def test_get_device_called(self, mock_get_device, mock_wc_contact):
#         request_params = {
#             'device_id': 'deviceid',
#             'design_id': 'designid',
#             'amount': 10
#         }
#         request = pyramidtesting.DummyRequest(params=request_params)
#         request.dbsession = MagicMock()
#         self._call(request)
#         mock_get_device.assert_called_once_with(request)

#     @patch('backend.views.userviews.wc_contact')
#     @patch('backend.views.userviews.get_device')
#     def test_wc_call(self, mock_get_device, mock_wc_contact):
#         amount = 10
#         request_params = {
#             'device_id': 'deviceid',
#             'design_id': 'designid',
#             'amount': amount
#         }
#         request = pyramidtesting.DummyRequest(params=request_params)
#         mdbsession = request.dbsession = MagicMock()
#         mock_query = mdbsession.query.return_value
#         mock_design = mock_query.get.return_value
#         mock_design.distribution_id = dist_id = 'distributionid'
#         mock_design.wc_id = design_wc_id = 'designwcid'
#         mock_device = mock_get_device.return_value
#         mock_user = mock_device.user
#         mock_user.wc_id = user_wc_id = 'userwcid'
#         self._call(request)
#         args = (request, 'POST', 'design/{0}/send'.format(design_wc_id))
#         params = {
#             'distribution_plan_id': dist_id,
#             'recipient_uid': 'wingcash:{0}'.format(user_wc_id),
#             'amount': amount
#         }
#         mock_wc_contact.assert_called_once_with(*args, params=params)

#     def test_string_amount(self):
#         amount = 'ten'
#         request_params = {
#             'device_id': 'deviceid',
#             'design_id': 'designid',
#             'amount': amount
#         }
#         request = pyramidtesting.DummyRequest(params=request_params)
#         with self.assertRaises(Invalid) as cm:
#             self._call(request)
#         e = cm.exception
#         expected_response = {
#             'amount': '"{0}" is not a number'.format(amount)
#         }
#         self.assertEqual(expected_response, e.asdict())

#     def test_negative_amount(self):
#         amount = -1
#         request_params = {
#             'device_id': 'deviceid',
#             'design_id': 'designid',
#             'amount': amount
#         }
#         request = pyramidtesting.DummyRequest(params=request_params)
#         with self.assertRaises(Invalid) as cm:
#             self._call(request)
#         e = cm.exception
#         expected_response = {
#             'amount': '{0}.0 is less than minimum value 0.01'.format(amount)
#         }
#         self.assertEqual(expected_response, e.asdict())

#     def test_invalid_design(self):
#         request_params = {
#             'device_id': 'invalid_device_id',
#             'design_id': 'designid',
#             'amount': 10
#         }
#         request = pyramidtesting.DummyRequest(params=request_params)
#         mdbsession = request.dbsession = MagicMock()
#         mock_query = mdbsession.query.return_value
#         mock_query.get.return_value = None
#         response = self._call(request)
#         expected_response = {'error': 'invalid_design'}
#         self.assertEqual(response, expected_response)

#     # TODO test wc_contact fails


class TestIsUser(TestCase):

    def _call(self, *args, **kw):
        return is_user(*args, **kw)

    def test_no_params(self):
        request = pyramidtesting.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {'device_id': 'Required'}
        self.assertEqual(expected_response, e.asdict())

    def test_invalid_device_id(self):
        request_params = {
            'device_id': 'asdf'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        response = self._call(request)
        self.assertFalse(response.get('is_user'))

    def test_valid_device_id(self):
        request_params = {
            'device_id': 'asdf'
        }
        request = pyramidtesting.DummyRequest(params=request_params)
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
        request = pyramidtesting.DummyRequest(params=request_params)
        mdbsession = request.dbsession = MagicMock()
        mdevice = MagicMock()
        mock_query = mdbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        mock_filter.return_value.first.return_value = mdevice
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))
