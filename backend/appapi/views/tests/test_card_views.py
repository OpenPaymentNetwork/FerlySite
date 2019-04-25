from backend.appapi.schemas import card_views_schemas as schemas
from backend.appapi.views.card_views import add_card
from backend.appapi.views.card_views import change_pin
from backend.appapi.views.card_views import delete_card
from backend.appapi.views.card_views import suspend_card
from backend.appapi.views.card_views import unsuspend_card
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


@patch('backend.appapi.views.card_views.get_wc_token')
@patch('backend.appapi.views.card_views.wc_contact')
class TestAddCard(TestCase):

    def _call(self, *args, **kw):
        return add_card(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'default_device_id',
            'pin': '1234',
            'pan': '4747474747474747'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.AddCardSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.AddCardSchema))

    @patch('backend.appapi.views.card_views.get_device')
    def test_get_wc_token_args(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_with(
            request, customer, permissions=['link_paycard'])

    def test_wc_contact_args(self, wc_contact, get_wc_token):
        access_token = get_wc_token.return_value
        card_params = {'pan': '4532015112830366', 'pin': '2345'}
        request = self._make_request(**card_params)
        self._call(request)
        wc_contact.assert_called_with(request, 'POST', 'wallet/paycard/link',
                                      params=card_params,
                                      access_token=access_token)

    def test_fail_wc_response(self, wc_contact, get_wc_token):
        wc_contact.return_value.json.return_value = {'linked': False}
        response = self._call(self._make_request())
        self.assertFalse(response['result'])

    def test_successful_wc_response(self, wc_contact, get_wc_token):
        wc_contact.return_value.json.return_value = {'linked': True}
        response = self._call(self._make_request())
        self.assertTrue(response['result'])


@patch('backend.appapi.views.card_views.get_wc_token')
@patch('backend.appapi.views.card_views.wc_contact')
class TestDeleteCard(TestCase):

    def _call(self, *args, **kw):
        return delete_card(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'default_device_id',
            'card_id': 'default_card_id'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.CardSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.CardSchema))

    @patch('backend.appapi.views.card_views.get_device')
    def test_get_wc_token_args(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_with(
            request, customer, permissions=['link_paycard'])

    def test_wc_contact_args(self, wc_contact, get_wc_token):
        access_token = get_wc_token.return_value
        card_params = {'card_id': '0bb0ed76a44e9204'}
        request = self._make_request(**card_params)
        self._call(request)
        wc_contact.assert_called_with(request, 'POST', 'wallet/paycard/delete',
                                      params=card_params,
                                      access_token=access_token)


@patch('backend.appapi.views.card_views.get_wc_token')
@patch('backend.appapi.views.card_views.wc_contact')
class TestChangePin(TestCase):

    def _call(self, *args, **kw):
        return change_pin(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'default_device_id',
            'pin': '1234',
            'card_id': 'default_card_id'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.ChangePinSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.ChangePinSchema))

    @patch('backend.appapi.views.card_views.get_device')
    def test_get_wc_token_args(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_with(
            request, customer, permissions=['link_paycard'])

    def test_wc_contact_args(self, wc_contact, get_wc_token):
        access_token = get_wc_token.return_value
        card_params = {'card_id': '0bb0ed76a44e9204', 'pin': '4321'}
        request = self._make_request(**card_params)
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/paycard/set-pin', params=card_params,
            access_token=access_token)


@patch('backend.appapi.views.card_views.get_wc_token')
@patch('backend.appapi.views.card_views.wc_contact')
class TestSuspendCard(TestCase):

    def _call(self, *args, **kw):
        return suspend_card(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'default_device_id',
            'card_id': 'default_card_id'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.CardSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.CardSchema))

    @patch('backend.appapi.views.card_views.get_device')
    def test_get_wc_token_args(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_with(
            request, customer, permissions=['link_paycard'])

    def test_wc_contact_args(self, wc_contact, get_wc_token):
        access_token = get_wc_token.return_value
        card_params = {'card_id': '0bb0ed76a44e9204'}
        request = self._make_request(**card_params)
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/paycard/suspend', params=card_params,
            access_token=access_token)


@patch('backend.appapi.views.card_views.get_wc_token')
@patch('backend.appapi.views.card_views.wc_contact')
class TestUnsuspendCard(TestCase):

    def _call(self, *args, **kw):
        return unsuspend_card(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'default_device_id',
            'card_id': 'default_card_id'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.CardSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.CardSchema))

    @patch('backend.appapi.views.card_views.get_device')
    def test_get_wc_token_args(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_with(
            request, customer, permissions=['link_paycard'])

    def test_wc_contact_args(self, wc_contact, get_wc_token):
        access_token = get_wc_token.return_value
        card_params = {'card_id': '0bb0ed76a44e9204'}
        request = self._make_request(**card_params)
        self._call(request)
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/paycard/unsuspend', params=card_params,
            access_token=access_token)
