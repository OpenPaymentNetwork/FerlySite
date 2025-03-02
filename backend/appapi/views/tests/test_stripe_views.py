
from backend.appapi.schemas import stripe_views_schemas as schemas
from backend.testing import add_device
from backend.testing import DBFixture
from colander import Invalid
from decimal import Decimal
from stripe.error import CardError
from stripe.error import InvalidRequestError
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class TestGetStripeCustomer(TestCase):

    def _make_request(self):
        request = pyramid.testing.DummyRequest()
        request.ferlysettings = MagicMock()
        return request

    def _call(self, request, stripe_id):
        from backend.appapi.views.stripe_views import get_stripe_customer
        return get_stripe_customer(request, stripe_id)

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
        retrieve.side_effect = InvalidRequestError('message', 'param')
        self.assertIsNone(self._call(self._make_request(), 'my_stripe_id'))

    @patch('backend.appapi.views.stripe_views.stripe')
    def test_customer_returned(self, stripe):
        stripe.Customer.retrieve.return_value = customer = 'found_customer'
        self.assertEqual(customer, self._call(self._make_request(), customer))


class TestListStripeSources(TestCase):

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest()
        return request

    def _call(self, *args, **kw):
        from backend.appapi.views.stripe_views import list_stripe_sources
        return list_stripe_sources(*args, **kw)

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_get_device_called(self, get_stripe_customer, get_device):
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_get_stripe_customer_params(self, get_stripe_customer, get_device):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_stripe_customer.assert_called_once_with(
            request, customer.stripe_id)

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_returns_correct_sources(self, get_stripe_customer, get_device):
        customer = get_stripe_customer.return_value
        obj1 = MagicMock()
        obj2 = MagicMock()
        customer.sources.data = [obj1, obj2]
        expected_sources = [{
            'id': obj1.id,
            'last_four': obj1.last4,
            'brand': obj1.brand
        }, {
            'id': obj2.id,
            'last_four': obj2.last4,
            'brand': obj2.brand
        }]
        response = self._call(self._make_request())
        self.assertEqual(response, {'sources': expected_sources})

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_new_stripe_customer(self, get_stripe_customer, get_device):
        get_stripe_customer.return_value = None
        response = self._call(self._make_request())
        self.assertEqual(response, {'sources': []})


class TestDeleteStripeSource(TestCase):

    def _make_request(self, **kw):
        request_params = {
            'source_id': 'default_source_id'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.get_params = params = MagicMock()
        params.return_value = schemas.DeleteSourceSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _call(self, *args, **kw):
        from backend.appapi.views.stripe_views import delete_stripe_source
        return delete_stripe_source(*args, **kw)

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_correct_schema_used(self, get_stripe_customer, get_device):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.DeleteSourceSchema))

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_get_device_called(self, get_stripe_customer, get_device):
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_get_stripe_customer_params(self, get_stripe_customer, get_device):
        customer = get_device.return_value.customer
        request = self._make_request()
        self._call(request)
        get_stripe_customer.assert_called_once_with(
            request, customer.stripe_id)

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_nonexistent_stripe_customer(self, get_stripe_customer, get_device):
        get_stripe_customer.return_value = None
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'nonexistent_customer'})

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_retrieve_params(self, get_stripe_customer, get_device):
        stripe_customer = get_stripe_customer.return_value
        retrieve = stripe_customer.sources.retrieve
        source_id = 'my_source_id'
        self._call(self._make_request(source_id=source_id))
        retrieve.assert_called_once_with(source_id)

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_delete_is_called(self, get_stripe_customer, get_device):
        retrieve = get_stripe_customer.return_value.sources.retrieve
        self._call(self._make_request())
        retrieve.assert_called_once()

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_deleted(self, get_stripe_customer, get_device):
        retrieve = get_stripe_customer.return_value.sources.retrieve
        retrieve.return_value.delete.return_value = {'deleted': True}
        response = self._call(self._make_request())
        self.assertTrue(response['result'])

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_not_deleted(self, get_stripe_customer, get_device):
        retrieve = get_stripe_customer.return_value.sources.retrieve
        retrieve.return_value.delete.return_value = {'deleted': False}
        response = self._call(self._make_request())
        self.assertFalse(response['result'])

    @patch('backend.appapi.views.stripe_views.get_device')
    @patch('backend.appapi.views.stripe_views.get_stripe_customer')
    def test_delete_error(self, get_stripe_customer, get_device):
        retrieve = get_stripe_customer.return_value.sources.retrieve
        retrieve.return_value.delete.return_value = {}
        response = self._call(self._make_request())
        self.assertFalse(response['result'])


@patch('backend.appapi.views.stripe_views.get_distributor_token')
@patch('backend.appapi.views.stripe_views.wc_contact')
@patch('backend.appapi.views.stripe_views.stripe')
@patch('backend.appapi.views.stripe_views.get_stripe_customer')
@patch('backend.appapi.views.stripe_views.get_device')
class TestPurchase(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _make_request(self, **kw):
        request_params = {
            'source_id': 'card_source',
            'design_id': 'default_design_id',
            'amount': 1.00,
            'fee': 2.00,
            'appdata.ferly.transactionType': 'purchase',
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        request.ferlysettings = MagicMock()
        params.return_value = schemas.PurchaseSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _add_design(self, fee=2):
        from backend.database.models import Design
        design = Design(
            id='default_design_id',
            wc_id='41',
            title="Default Design",
            fee=fee,
        )
        self.dbsession.add(design)
        self.dbsession.flush()
        return design

    def _call(self, *args, **kw):
        from backend.appapi.views.stripe_views import purchase
        return purchase(*args, **kw)

    def test_correct_schema_used(self, *args):
        request = self._make_request()
        request.ferlysettings.stripe_api_key = 'my_stripe_api_key'
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.PurchaseSchema))

    def test_invalid_design(self, get_device, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request(design_id='my_design_id')
        response = self._call(request)
        self.assertEqual(response, {'error': 'invalid_design'})

    def test_get_stripe_customer_params(
            self, get_device, get_stripe_customer, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        request = self._make_request()
        customer = get_device.return_value.customer
        self._call(request)
        get_stripe_customer.assert_called_once_with(
            request, customer.stripe_id)

    def test_create_new_stripe_customer(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        get_stripe_customer.return_value = None
        request = self._make_request()
        self._call(request)
        stripe.Customer.create.assert_called_once_with(
            api_key=request.ferlysettings.stripe_api_key)

    def test_new_stripe_customer_sets_customer_stripe_id(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        get_stripe_customer.return_value = None
        customer = get_device.return_value.customer
        stripe_customer = stripe.Customer.create.return_value
        self._call(self._make_request())
        self.assertEqual(customer.stripe_id, stripe_customer.id)

    def test_new_source(self, get_device, get_stripe_customer, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        customer = get_stripe_customer.return_value
        request = self._make_request(source_id='tok_source')
        self._call(request)
        customer.sources.create.assert_called_once_with(source='tok_source')

    def test_create_source_error(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        customer = get_stripe_customer.return_value
        customer.sources.create.side_effect = CardError(
            'message', 'param', 'code')
        request = self._make_request(source_id='tok_source')
        response = self._call(request)
        self.assertFalse(response['result'], False)
        self.assertFalse(stripe.Charge.create.called)

    def test_invalid_source(self, get_device, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        request = self._make_request(source_id='bad_source')
        with self.assertRaises(Invalid):
            self._call(request)

    def test_new_charge_card_id(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        card = get_stripe_customer.return_value.sources.create.return_value
        self._call(self._make_request(source_id='tok_source'))
        self.assertEqual(stripe.Charge.create.call_args[1]['source'], card.id)

    def test_existing_charge_card_id(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        source = 'card_source'
        self._call(self._make_request(source_id=source))
        self.assertEqual(stripe.Charge.create.call_args[1]['source'], source)

    def test_amount_conversion(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design(fee=0)
        # A float SchemaNode would convert $18.90 to 1889
        self._call(self._make_request(amount=18.90, fee=0))
        self.assertEqual(stripe.Charge.create.call_args[1]['amount'], 1890)

    def test_amount_type(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        self._call(self._make_request())
        amount_arg = stripe.Charge.create.call_args[1]['amount']
        self.assertTrue(isinstance(amount_arg, int))

    def test_charge_customer(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        customer = get_stripe_customer.return_value
        self._call(self._make_request())
        charge_args = stripe.Charge.create.call_args[1]
        self.assertEqual(charge_args['customer'], customer.id)

    def test_charge_args(
            self, get_device, get_stripe_customer, stripe, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        request = self._make_request()
        self._call(request)
        charge_args = stripe.Charge.create.call_args[1]
        expected_args = {
            'currency': 'USD',
            'capture': False,
            'api_key': request.ferlysettings.stripe_api_key,
            'statement_descriptor': 'Ferly Card App'
        }
        for arg in expected_args:
            with self.subTest():
                self.assertEqual(charge_args[arg], expected_args[arg])

    def test_charge_card_error(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        stripe.Charge.create.side_effect = CardError(
            'message', 'param', 'code')
        response = self._call(self._make_request())
        self.assertFalse(response['result'])
        self.assertFalse(wc_contact.called)

    def test_charge_not_paid(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        stripe.Charge.create.return_value.paid = False
        response = self._call(self._make_request())
        self.assertFalse(response['result'])
        self.assertFalse(wc_contact.called)

    def test_wc_contact_args(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        design = self._add_design(fee=Decimal('1.44'))
        amount = Decimal('10.85')
        fee = Decimal('1.44')
        request = self._make_request(amount=amount, fee=fee)
        customer = get_device.return_value.customer
        charge = stripe.Charge.create.return_value
        self._call(request)
        expected_args = {
            'distribution_plan_id': design.distribution_id,
            'recipient_uid': 'wingcash:' + customer.wc_id,
            'amount': str(amount),
            'appdata.ferly.convenience_fee': str(fee),
            'appdata.ferly.stripe_brand':
                charge.payment_method_details.card.brand,
            'appdata.ferly.stripe_last4':
                charge.payment_method_details.card.last4,
            'appdata.ferly.transactionType': 'purchase',
        }
        args = wc_contact.call_args
        self.assertEqual(
            (request, 'POST', 'design/{0}/send'.format(design.wc_id)), args[0])
        self.assertEqual(args[1]['params'], expected_args)

    def test_wc_contact_error(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        wc_contact.return_value.status_code = 500
        charge = stripe.Charge.create.return_value
        response = self._call(self._make_request())
        self.assertFalse(response['result'])
        self.assertFalse(charge.capture.called)

    def test_capture(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        wc_contact.return_value.status_code = 200
        capture = stripe.Charge.create.return_value.capture
        capture.return_value.paid = False
        response = self._call(self._make_request())
        self.assertTrue(capture.called)
        self.assertFalse(response['result'])

    def test_failed_capture(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        wc_contact.return_value.status_code = 200
        capture = stripe.Charge.create.return_value.capture
        capture.return_value.paid = True
        response = self._call(self._make_request())
        self.assertTrue(response['result'])

    def test_fee_mismatch(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design()
        response = self._call(self._make_request(amount=18.90, fee=2.21))
        self.assertEqual(response, {'error': 'fee_mismatch'})

    def test_charge_amount(
            self, get_device, get_stripe_customer, stripe, wc_contact, *args):
        get_device.return_value = add_device(self.dbsession)[0]
        self._add_design(fee=3)
        self._call(self._make_request(amount=18.90, fee=3.00))
        self.assertEqual(stripe.Charge.create.call_args[1]['amount'], 2190)
