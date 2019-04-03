from backend.appapi.views.stripe_views import get_customer
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing
from stripe.error import InvalidRequestError


class TestGetCustomer(TestCase):

    def _make_request(self):
        request = pyramid.testing.DummyRequest()
        request.ferlysettings = MagicMock()
        return request

    def _call(self, request, stripe_id):
        return get_customer(request, stripe_id)

    def test_without_stripe_id(self):
        self.assertIsNone(self._call(self._make_request(), ''))

    @patch('backend.appapi.views.stripe_views.stripe')
    def test_retrieve_params(self, stripe):
        stripe_id = 'my_stripe_id'
        request = self._make_request()
        self._call(request, stripe_id)
        stripe.Customer.retrieve.assert_called_once_with(
            stripe_id, api_key=request.ferlysettings.stripe_api_key)

    @patch('backend.appapi.views.stripe_views.stripe')
    def test_retrieve_exception(self, stripe):
        retrieve = stripe.Customer.retrieve
        retrieve.side_effect = Exception(InvalidRequestError(
            'message', 'param'))
        # with self.assertRaises(InvalidRequestError):
        #     self._call(self._make_request(), 'my_stripe_id')
        # try:
        customer = self._call(self._make_request(), 'my_stripe_id')
        print("customer", customer)
            # raise InvalidRequestError('m', 'p')
        # except Exception as e:
        #     print("e", e)
        #     print("heyo!")

    # test if stripe.error.InvalidRequestError: None is returned
    # test retrieve value is returned



# class TestListStripeSources(TestCase):

