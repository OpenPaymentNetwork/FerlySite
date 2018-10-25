from backend.views.braintreeviews import create_purchase
from backend.views.braintreeviews import request_token
from colander import Invalid
from pyramid import testing as pyramidtesting
from unittest import TestCase
# from unittest.mock import call
# from unittest.mock import MagicMock
# from unittest.mock import patch


class TestRequestToken(TestCase):

    def _call(self, *args, **kw):
        return request_token(*args, **kw)

    # def test_no_params(self):
    #     request = pyramidtesting.DummyRequest()
    #     with self.assertRaises(Invalid) as cm:
    #         self._call(request)
    #     e = cm.exception
    #     expected_response = {'device_id': 'Required'}
    #     self.assertEqual(expected_response, e.asdict())

    # assert gateway.customer.find called with user.id
    # assert gateway.customer.create not called unless BT.notfounderror raised
    # assert gateway.customer.create called with user.id as id
    # assert gateway.client_token.generate is called with proper customer.id
    # assert gateway.client_token.generate result is in response as 'token'


class TestCreatePurchase(TestCase):

    def _call(self, *args, **kw):
        return create_purchase(*args, **kw)

    # def test_no_params(self):
    #     request = pyramidtesting.DummyRequest()
    #     with self.assertRaises(Invalid) as cm:
    #         self._call(request)
    #     e = cm.exception
    #     expected_response = {'device_id': 'Required'}
    #     self.assertEqual(expected_response, e.asdict())

    # assert invalid_design is raised if dbsession.query of design_id is None
    # assert design is dbsession.get(params['design_id])
    # assert gateway.transaction.sale params
    # assert gateway.transaction.sale not submitting for settlement
    # assert wc_contact post params
    # assert failed response if wc_contact fails, and transaction not submitted for settlement
    # assert gateway.transaction.submit_for_settlement called with proper params if wc_contact passes
