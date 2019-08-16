
from backend.testing import add_device
from backend.testing import DBFixture
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPUnauthorized
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch
import datetime
import logging
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class Test_get_device_token(TestCase):

    def _call(self, *args, **kw):
        from ..utils import get_device_token
        return get_device_token(*args, **kw)

    def test_missing_token_when_not_required(self):
        request = pyramid.testing.DummyRequest()
        self.assertIsNone(self._call(request, params={}))

    def test_valid_token_with_authorization_header(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceid0defaultdeviceid0',
        })
        result = self._call(request, {})
        self.assertEqual('defaultdeviceid0defaultdeviceid0', result)

    def test_valid_token_with_param(self):
        request = pyramid.testing.DummyRequest()
        result = self._call(request, params={
            'device_id': 'defaultdeviceid0defaultdeviceid0',
        })
        self.assertEqual('defaultdeviceid0defaultdeviceid0', result)

    def test_token_required_but_missing(self):
        request = pyramid.testing.DummyRequest(headers={})
        with self.assertRaises(HTTPBadRequest) as cm:
            self._call(request, {}, required=True)
        self.assertRegexpMatches(
            str(cm.exception.json_body), r'device_token_required')

    def test_token_too_short_but_not_required(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer id0',
        })
        result = self._call(request, {})
        self.assertIsNone(result)

    def test_token_too_short_when_required(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer id0',
        })
        with self.assertRaises(HTTPBadRequest) as cm:
            self._call(request, {}, required=True)
        self.assertRegexpMatches(
            str(cm.exception.json_body), r'device_token_too_short')

    def test_token_too_long_but_not_required(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer ' + '1' * 201,
        })
        result = self._call(request, {})
        self.assertIsNone(result)

    def test_token_too_long_when_required(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer ' + '1' * 201,
        })
        with self.assertRaises(HTTPBadRequest) as cm:
            self._call(request, {}, required=True)
        self.assertRegexpMatches(
            str(cm.exception.json_body), r'device_token_too_long')


class TestGetDevice(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.utils import get_device
        return get_device(*args, **kw)

    def test_invalid_device_id(self):
        request = pyramid.testing.DummyRequest()
        request.dbsession = self.dbsession
        with self.assertRaises(HTTPUnauthorized):
            self._call(request, params={})

    def test_valid_device_with_authorization_header(self):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceid0defaultdeviceid0',
        })
        dbsession = request.dbsession = self.dbsession
        device = add_device(dbsession)
        result = self._call(request, {})
        self.assertEqual(device, result)

    def test_valid_device_with_param(self):
        request = pyramid.testing.DummyRequest()
        dbsession = request.dbsession = self.dbsession
        device = add_device(dbsession)
        result = self._call(request, params={
            'device_id': 'defaultdeviceid0defaultdeviceid0',
        })
        self.assertEqual(device, result)

    def test_device_not_found(self):
        request = pyramid.testing.DummyRequest()
        dbsession = request.dbsession = self.dbsession
        add_device(dbsession)
        with self.assertRaises(HTTPUnauthorized):
            self._call(request, params={
                'device_id': 'fakedeviceid' * 4,
            })

    def test_update_device_used_yesterday(self):
        from backend.database.models import now_utc
        request = pyramid.testing.DummyRequest()
        dbsession = request.dbsession = self.dbsession
        device = add_device(dbsession)
        device.last_used = (
            datetime.datetime.utcnow() - datetime.timedelta(days=1))
        result = self._call(request, params={
            'device_id': 'defaultdeviceid0defaultdeviceid0',
        })
        self.assertEqual(device, result)
        self.assertIs(now_utc, device.last_used)

    def test_no_update_device_used_2_seconds_ago(self):
        request = pyramid.testing.DummyRequest()
        dbsession = request.dbsession = self.dbsession
        device = add_device(dbsession)
        last_used = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)
        device.last_used = last_used
        result = self._call(request, params={
            'device_id': 'defaultdeviceid0defaultdeviceid0',
        })
        self.assertEqual(device, result)
        self.assertEqual(last_used, device.last_used)


@patch('requests.post')
class TestNotifyCustomer(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.utils import notify_customer
        args = {
            'request': Mock(),
            'customer': Mock(),
            'title': 'default_title',
            'body': 'default_body',
        }
        args.update(**kw)
        return notify_customer(**args)

    def test_no_devices_found(self, post):
        request = Mock()
        request.dbsession = self.dbsession
        self._call(request=request, customer=Mock(id='123'))
        post.assert_not_called()

    def test_device_without_expo_token(self, post):
        device = add_device(self.dbsession)
        request = Mock()
        request.dbsession = self.dbsession
        device.expo_token = None
        self._call(request=request, customer=Mock(id=device.customer.id))
        post.assert_not_called()

    def test_post_args(self, post):
        device = add_device(self.dbsession)
        request = Mock()
        request.dbsession = self.dbsession
        device.expo_token = 'my_expo_token'
        self._call(
            request=request,
            customer=device.customer,
            title='my_title',
            body='my_body')
        expected_notification = {
            'to': 'my_expo_token',
            'title': 'my_title',
            'body': 'my_body',
            'sound': 'default'
        }
        post.assert_called_once()
        call_ordered, call_kw = post.call_args
        self.assertEqual(
            ('https://exp.host/--/api/v2/push/send',),
            call_ordered)
        self.assertEqual([expected_notification], call_kw['json'])
        self.assertEqual({
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/json',
        }, call_kw['headers'])

    def test_channel_id(self, post):
        device = add_device(self.dbsession)
        request = Mock()
        request.dbsession = self.dbsession
        device.expo_token = 'my_expo_token'
        self._call(
            request=request,
            customer=device.customer,
            title='my_title',
            body='my_body',
            channel_id='my_channel_id')
        expected_notification = {
            'to': 'my_expo_token',
            'title': 'my_title',
            'body': 'my_body',
            'sound': 'default',
            'channelId': 'my_channel_id'
        }
        post.assert_called_once()
        call_ordered, call_kw = post.call_args
        self.assertEqual([expected_notification], call_kw['json'])

    def test_log_exception(self, post):
        device = add_device(self.dbsession)
        request = Mock()
        request.dbsession = self.dbsession
        device.expo_token = 'my_expo_token'

        post.return_value = Mock(
            raise_for_status=Mock(side_effect=ValueError('synthetic')))

        with self.assertLogs("backend.appapi.utils", level=logging.ERROR):
            self._call(
                request=request,
                customer=device.customer,
                title='my_title',
                body='my_body')


@patch('backend.appapi.utils.wc_contact')
class TestGetWCToken(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.utils import get_wc_token
        return get_wc_token(*args, **kw)

    def test_params(self, mock_wc_contact):
        request = pyramid.testing.DummyRequest()
        customer = MagicMock()
        customer.wc_id = 'wc_id'
        self._call(request, customer)
        params = {
            'uid': 'wingcash:' + customer.wc_id,
            'concurrent': True,
            'permissions': []}
        args = (request, 'POST', 'p/token', params)
        kw = {'auth': True}
        mock_wc_contact.assert_called_once_with(*args, **kw)

    def test_permissions(self, wc_contact):
        request = pyramid.testing.DummyRequest()
        perms = ['my_permission']
        self._call(request, MagicMock(), permissions=perms)
        self.assertEqual(perms, wc_contact.call_args[0][3]['permissions'])

    def test_no_token(self, mock_wc_contact):
        request = pyramid.testing.DummyRequest()
        mock_wc_contact.return_value.json.return_value = {}
        customer = MagicMock()
        customer.wc_id = 'wc_id'
        response = self._call(request, customer)
        self.assertIsNone(response)

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
