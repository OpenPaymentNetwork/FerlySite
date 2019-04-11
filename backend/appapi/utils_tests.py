from backend.database.models import Device
from backend.appapi.utils import get_device
from backend.appapi.utils import get_wc_token
from backend.appapi.utils import notify_customer
from pyramid.httpexceptions import HTTPUnauthorized
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


@patch('requests.post')
class TestNotifyCustomer(TestCase):

    def _call(self, *args, **kw):
        args = {
            'request': MagicMock(),
            'customer': MagicMock(),
            'title': 'default_title',
            'body': 'default_body',
        }
        args.update(**kw)
        return notify_customer(**args)

    def test_query_device(self, post):
        request = MagicMock()
        query = request.dbsession.query
        self._call(request=request)
        query.assert_called_once_with(Device)

    def test_filter_on_customer_id(self, post):
        request = MagicMock()
        mock_filter = request.dbsession.query.return_value.filter
        customer = MagicMock()
        self._call(request=request, customer=customer)
        expression = Device.customer_id == customer.id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    def test_search_for_all_devices(self, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        self._call(request=request)
        mock_all.assert_called_once()

    def test_no_devices_found(self, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        mock_all.return_value = []
        self._call(request=request)
        post.assert_not_called()

    def test_no_valid_devices_found(self, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        device1 = MagicMock()
        device1.expo_token = None
        mock_all.return_value = [device1]
        self._call(request=request)
        post.assert_not_called()

    @patch('json.dumps')
    def test_notification_args(self, dumps, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        device1 = MagicMock()
        device1.expo_token = 'my_expo_token'
        mock_all.return_value = [device1]
        self._call(request=request, title='my_title', body='my_body')
        expected_notification = {
            'to': 'my_expo_token',
            'title': 'my_title',
            'body': 'my_body',
            'sound': 'default'
        }
        self.assertEqual([expected_notification], dumps.call_args[0][0])

    @patch('json.dumps')
    def test_channel_id(self, dumps, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        device1 = MagicMock()
        device1.expo_token = 'my_expo_token'
        mock_all.return_value = [device1]
        self._call(request=request, title='my_title', body='my_body',
                   channel_id='my_channel_id')
        expected_notification = {
            'to': 'my_expo_token',
            'title': 'my_title',
            'body': 'my_body',
            'sound': 'default',
            'channelId': 'my_channel_id'
        }
        self.assertEqual([expected_notification], dumps.call_args[0][0])

    def test_url(self, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        device1 = MagicMock()
        device1.expo_token = 'my_expo_token'
        mock_all.return_value = [device1]
        self._call(request=request)
        self.assertEqual(
            'https://exp.host/--/api/v2/push/send', post.call_args[0][0])

    def test_headers(self, post):
        request = MagicMock()
        mock_all = request.dbsession.query.return_value.filter.return_value.all
        device1 = MagicMock()
        device1.expo_token = 'my_expo_token'
        mock_all.return_value = [device1]
        self._call(request=request)
        expected_headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/json',
        }
        self.assertEqual(expected_headers, post.call_args[1]['headers'])


class TestGetWCToken(TestCase):

    def _call(self, *args, **kw):
        return get_wc_token(*args, **kw)

    @patch('backend.appapi.utils.wc_contact')
    def test_params(self, mock_wc_contact):
        request = pyramid.testing.DummyRequest()
        customer = MagicMock()
        customer.wc_id = 'wc_id'
        self._call(request, customer)
        params = {'uid': 'wingcash:' + customer.wc_id, 'concurrent': True}
        args = (request, 'GET', 'p/token', params)
        kw = {'auth': True}
        mock_wc_contact.assert_called_once_with(*args, **kw)

    @patch('backend.appapi.utils.wc_contact')
    def test_no_token(self, mock_wc_contact):
        request = pyramid.testing.DummyRequest()
        mock_wc_contact.return_value.json.return_value = {}
        customer = MagicMock()
        customer.wc_id = 'wc_id'
        response = self._call(request, customer)
        self.assertIsNone(response)

    @patch('backend.appapi.utils.wc_contact')
    def test_response(self, mock_wc_contact):
        request = pyramid.testing.DummyRequest()
        token = '123'
        mock_wc_contact.return_value.json.return_value = {
            'access_token': token
        }
        customer = MagicMock()
        customer.wc_id = 'wc_id'
        response = self._call(request, customer)
        self.assertEqual(response, token)


class TestGetDevice(TestCase):

    def _call(self, *args, **kw):
        return get_device(*args, **kw)

    def test_invalid_device_id(self):
        request = pyramid.testing.DummyRequest()
        mdbsession = request.dbsession = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPUnauthorized):
            self._call(request, params={})

    def test_device_has_no_customer(self):
        request = pyramid.testing.DummyRequest()
        mdbsession = request.dbsession = MagicMock()
        mdevice = MagicMock()
        mdevice.customer = None
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = mdevice
        with self.assertRaises(HTTPUnauthorized):
            self._call(request, params={})

    def test_return_value(self):
        request = pyramid.testing.DummyRequest()
        mdbsession = request.dbsession = MagicMock()
        mdevice = MagicMock()
        mock_query = mdbsession.query.return_value
        mock_query.filter.return_value.first.return_value = mdevice
        response = self._call(request, params={})
        self.assertEqual(mdevice, response)

    def test_query(self):
        request = pyramid.testing.DummyRequest()
        mdbsession = request.dbsession = MagicMock()
        mdevice = MagicMock()
        mock_query = mdbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        mock_filter.return_value.first.return_value = mdevice
        device_id = '123'
        self._call(request, params={'device_id': device_id})
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))
