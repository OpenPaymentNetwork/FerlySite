from backend.database.models import Device
from backend.appapi.utils import get_device
from backend.appapi.utils import get_wc_token
from pyramid.httpexceptions import HTTPUnauthorized
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


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
