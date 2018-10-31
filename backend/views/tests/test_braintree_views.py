from backend.views.braintreeviews import create_purchase
from backend.views.braintreeviews import request_token
from braintree.exceptions.not_found_error import NotFoundError as btNotFound
from colander import Invalid
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestRequestToken(TestCase):

    def _call(self, *args, **kw):
        return request_token(*args, **kw)

    def test_device_id_required(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(request)

    @patch('backend.views.braintreeviews.gateway')
    @patch('backend.views.braintreeviews.get_device')
    def test_find_by_user_id(self, get_device, gateway):
        mock_user = get_device.return_value.user
        request = pyramid.testing.DummyRequest(params={'device_id': 'string'})
        self._call(request)
        gateway.customer.find.assert_called_with(str(mock_user.id))

    @patch('backend.views.braintreeviews.gateway')
    @patch('backend.views.braintreeviews.get_device')
    def test_create_new_customer(self, get_device, gateway):
        gateway.customer.find.side_effect = btNotFound()
        mock_user = get_device.return_value.user
        request = pyramid.testing.DummyRequest(params={'device_id': 'string'})
        result = gateway.customer.create.return_value
        self._call(request)
        gateway.customer.create.assert_called_with({'id': str(mock_user.id)})
        gateway.client_token.generate.assert_called_with({
            'customer_id':  result.customer.id})

    @patch('backend.views.braintreeviews.gateway')
    @patch('backend.views.braintreeviews.get_device')
    def test_generate_called_with_customer_id(self, get_device, gateway):
        request = pyramid.testing.DummyRequest(params={'device_id': 'string'})
        customer = gateway.customer.find.return_value
        self._call(request)
        gateway.client_token.generate.assert_called_with({
            'customer_id': customer.id})

    @patch('backend.views.braintreeviews.gateway')
    @patch('backend.views.braintreeviews.get_device')
    def test_token_in_response(self, get_device, gateway):
        request = pyramid.testing.DummyRequest(params={'device_id': 'string'})
        client_token = gateway.client_token.generate.return_value
        response = self._call(request)
        self.assertEqual(response, {'token': client_token})


class TestCreatePurchase(TestCase):

    def _call(self, *args, **kw):
        return create_purchase(*args, **kw)

    def make_request(self, **kw):
        params = {
            'device_id': 'defaultdeviceid',
            'design_id': 'defaultdesignid',
            'amount': 1.0,
            'nonce': 'defaultnonce'
        }
        params.update(**kw)
        request = pyramid.testing.DummyRequest(params=params)
        request.dbsession = MagicMock()
        return request

    def test_amount_required(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaisesRegex(Invalid, "'amount': 'Required'"):
            self._call(request)

    def test_amount_must_be_positive(self):
        request = pyramid.testing.DummyRequest(params={'amount': 0})
        error = "0.0 is less than minimum value 0.01"
        with self.assertRaisesRegex(Invalid, "'amount': '{0}'".format(error)):
            self._call(request)

    def test_amount_must_be_number(self):
        amount = 'abc'
        request = pyramid.testing.DummyRequest(params={'amount': amount})
        with self.assertRaisesRegex(
                Invalid, "'amount': '\"{0}\" is not a number'".format(amount)):
            self._call(request)

    def test_nonce_required(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaisesRegex(Invalid, "'nonce': 'Required'"):
            self._call(request)

    def test_design_id_required(self):
        request = pyramid.testing.DummyRequest()
        with self.assertRaisesRegex(Invalid, "'design_id': 'Required'"):
            self._call(request)

    def test_invalid_design_id(self):
        request = self.make_request()
        request.dbsession = mdbsession = MagicMock()
        mdbsession.query.return_value.get.return_value = None
        response = self._call(request)
        self.assertEqual(response, {'error': 'invalid_design'})

    @patch('backend.views.braintreeviews.wc_contact')
    @patch('backend.views.braintreeviews.gateway')
    def test_transaction_creation_args(self, gateway, wc_contact):
        request = self.make_request()
        self._call(request)
        expected_args = {
            'amount': '1.0',
            'payment_method_nonce': 'defaultnonce',
            'options': {'store_in_vault_on_success': True}
        }
        gateway.transaction.sale.assert_called_with(expected_args)

    @patch('backend.views.braintreeviews.gateway')
    def test_transaction_creation_fails(self, gateway):
        gateway.transaction.sale.return_value.is_success = False
        response = self._call(self.make_request())
        self.assertEqual(response, {'result': False})

    @patch('backend.views.braintreeviews.wc_contact')
    @patch('backend.views.braintreeviews.gateway')
    @patch('backend.views.braintreeviews.get_device')
    def test_wc_contact_params(self, get_device, gateway, wc_contact):
        request = self.make_request()
        mock_design = request.dbsession.query.return_value.get.return_value
        mock_design.distribution_id = 'distribution_id'
        mock_design.id = 'wc_id'
        mock_user = get_device.return_value.user
        self._call(request)
        wc_contact.assert_called_with(
            request,
            'POST',
            'design/{0}/send'.format(mock_design.wc_id),
            params={
                'distribution_plan_id': mock_design.distribution_id,
                'recipient_uid': 'wingcash:' + mock_user.wc_id, 'amount': 1.0}
        )

    @patch('backend.views.braintreeviews.wc_contact')
    @patch('backend.views.braintreeviews.gateway')
    def test_submit_on_success(self, gateway, wc_contact):
        result = gateway.transaction.sale.return_value
        self._call(self.make_request())
        gateway.transaction.submit_for_settlement.assert_called_with(
            result.transaction.id)

    @patch('backend.views.braintreeviews.wc_contact')
    @patch('backend.views.braintreeviews.gateway')
    def test_response_on_submit(self, gateway, wc_contact):
        result = gateway.transaction.submit_for_settlement.return_value
        response = self._call(self.make_request())
        self.assertEqual(response, {'result': result.is_success})
