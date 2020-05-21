
from backend.appapi.schemas import app_views_schemas as schemas
from backend.database.models import Design
from backend.testing import DBFixture
from unittest import TestCase
from backend.testing import add_deviceForCustomer11
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()

@patch('backend.appapi.views.app_views.get_device')
@patch('backend.appapi.views.app_views.wc_contact')
class TestLocationsCard(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.app_views import locations
        return locations(*args, **kw)

    def _make_request(self, **params):
        request_params = {'design_id': 'default_design_id'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.LocationsSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_location(self, **kw):
        location = {
            'title': 'default_title',
            'address': 'default_address',
            'latitude': 'default_latitude',
            'longitude': 'default_longitude'
        }
        location.update(**kw)
        return location

    def _add_design(self):
        from backend.database.models import Design
        dbsession = self.dbsession
        design = Design(
            wc_id='41',
            title='Test Design',
            fee='1.20',
        )
        dbsession.add(design)
        dbsession.flush()  # Assign design.id
        return design

    def test_correct_schema_used(self, wc_contact, get_device):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.LocationsSchema))

    def test_invalid_design(self, wc_contact, get_device):
        request = self._make_request()
        response = self._call(request)
        self.assertEqual({'error': 'invalid_design'}, response)

    def test_wc_contact_args(self, wc_contact, get_device):
        design = self._add_design()
        request = self._make_request(design_id=design.id)
        self._call(request)
        wc_contact.assert_called_with(
            request,
            'GET',
            '/design/{0}/redeemers'.format(design.wc_id),
            anon=True)

    def test_response(self, wc_contact, get_device):
        design = self._add_design()
        location = self._make_location()
        wc_contact.return_value.json.return_value = [location]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual([location], response['locations'])

    def test_unwanted_attributes_ignored(self, wc_contact, get_device):
        design = self._add_design()
        location = self._make_location()
        revised_location = location.copy()
        revised_location['unwanted_key'] = 'unwanted_value'
        wc_contact.return_value.json.return_value = [revised_location]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual([location], response['locations'])

    def test_multiple_locations(self, wc_contact, get_device):
        design = self._add_design()
        locations = wc_contact.return_value.json.return_value = [
            self._make_location(title='title1', address='address1'),
            self._make_location(title='title2', address='address2')
        ]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual(locations, response['locations'])


@patch('backend.appapi.views.app_views.get_device')
class TestGetFerlyCashDesign(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.app_views import get_ferly_cash_design
        return get_ferly_cash_design(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def _add_design(self):
        from backend.database.models import Design
        dbsession = self.dbsession
        design = Design(
            wc_id='41',
            title='Ferly Cash',
            fee='1.20',
        )
        dbsession.add(design)
        dbsession.flush()  # Assign design.id
        return design

    def test_get_device_called(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_design()
        self._call(request)
        get_device.assert_called()

    def test_got_Ferly_Cash_design(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_design()
        response = self._call(request)
        self.assertEqual(response.get('title'), "Ferly Cash")

@patch('backend.appapi.views.app_views.get_device')
class TestListLoyaltyDesigns(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.app_views import list_Loyalty_designs
        return list_Loyalty_designs(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def _add_designs(self):
        from backend.database.models import Design
        dbsession = self.dbsession
        design = Design(
            wc_id='41',
            title='Best Buy Loyalty',
            fee='1.20',
        )
        dbsession.add(design)
        dbsession.flush()  # Assign design.id
        design = Design(
            wc_id='42',
            title='Best Buy',
            fee='1.20',
        )
        dbsession.add(design)
        dbsession.flush()  # Assign design.id
        return design

    def test_get_device_called(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_designs()
        self._call(request)
        get_device.assert_called()

    def test_got_Ferly_Cash_design(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_designs()
        response = self._call(request)
        self.assertEqual(response[0].get('title'), "Best Buy Loyalty")
        self.assertEqual(len(response),1)

@patch('backend.appapi.views.app_views.get_device')
class TestListDesigns(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.app_views import list_designs
        return list_designs(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def _add_designs(self):
        from backend.database.models import Design
        dbsession = self.dbsession
        design = Design(
            wc_id='41',
            title='Walmart',
            fee='1.20',
            listable=True
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='42',
            title='Best Buy',
            fee='1.20',
            listable=False
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='42',
            title='Shopco',
            fee='1.20',
            listable=True
        )
        dbsession.add(design)
        dbsession.flush()
        return design

    def test_get_device_called(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_designs()
        self._call(request)
        get_device.assert_called()

    def test_got_designs(self, get_device):
        get_device.return_value = add_deviceForCustomer11(self.dbsession)[0]
        request = self._make_request()
        self._add_designs()
        response = self._call(request)
        self.assertEqual(len(response),2)

class TestRedemptionNotification(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.app_views import redemption_notification
        return redemption_notification(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'source_url': '/p/1/webhook',
            'transfers': [],
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        settings = request.ferlysettings = MagicMock()
        settings.environment = params.get('environment', 'staging')
        settings.wingcash_profile_id = 1
        settings.distributor_uid = 10
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        return request

    def _add_recipient(self, wc_id='12', username='friend'):
        from backend.database.models import Customer
        dbsession = self.dbsession
        recipient = Customer(
            wc_id=wc_id,
            first_name='Friend',
            last_name='User',
            username=username,
        )
        dbsession.add(recipient)
        dbsession.flush()  # Assign recipient.id
        return recipient

    def _add_notification(self, customer_id):
        from backend.database.models import Notification
        dbsession = self.dbsession
        notification = Notification(
            id='12',
            transfer_id='6',
            customer_id=customer_id,
        )
        dbsession.add(notification)
        dbsession.flush()  # Assign recipient.id
        return notification

    def _add_designs(self):
        from backend.database.models import Design
        dbsession = self.dbsession
        design = Design(
            wc_id='41',
            title='Walmart',
            fee='1.20',
            listable=True
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='42',
            title='Best Buy',
            fee='1.20',
            listable=False
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='43',
            title='Shopco',
            fee='1.20',
            listable=True
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='1',
            title='Ferly Cash',
            fee='0',
            listable=False
        )
        dbsession.add(design)
        dbsession.flush()
        design = Design(
            wc_id='2',
            title='Ferly Rewards',
            fee='0',
            listable=False
        )
        dbsession.add(design)
        dbsession.flush()
        
        return design

    @patch('backend.appapi.views.app_views.log.warning')
    def test_source_url(self, warning):
        request = self._make_request(source_url = '/p/2/webhook')
        response = self._call(request)
        self.assertEqual(response,{})
        warning.assert_called_once()

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_skip(self, notify_customer):
        request = self._make_request(transfers=[{'appdata.ferly.type': 'skip'}])
        response = self._call(request)
        notify_customer.assert_not_called()
        self.assertEqual(response,{})
    
    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_completed(self, exception, notify_customer):
        result = {
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': False,
            'movements': [{'loops': [{'loop_id': '1', 'currency': '1.00'}]}],
            'id': '6'
        }
        request = self._make_request(transfers=[result])
        response = self._call(request)
        notify_customer.assert_not_called()
        exception.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_trade(self, notify_customer):
        request = self._make_request(transfers=[{'workflow_type': 'trade'}])
        response = self._call(request)
        notify_customer.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_ach_confirm(self, notify_customer):
        achResult = {
            'odfi': '123456789',
            'odfi_name': 'test bank',
            'credits': ['.05'],
            'debits': ['.05'],
            'recipient_id': '12',
            'workflow_type': 'receive_ach_confirm',
            'completed': True
        }
        recipient = self._add_recipient()
        body = 'ACH confirmation received from ' + 'test bank' + '.'
        request = self._make_request(transfers = [achResult])
        response = self._call(request)
        self.assertEqual(response,{})
        notify_customer.assert_called_with(request, recipient, 'ACH Confirmation', body,
                    channel_id='card-used', data={'type': 'ach_confirmation', 'odfi': '123456789',
                    'odfi_name': 'test bank', 'credits': ['.05'], 'debits': ['.05']})

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_ach_prenote(self, notify_customer):
        achResult = {
            'odfi': '123456789',
            'odfi_name': 'test bank',
            'recipient_id': '12',
            'workflow_type': 'receive_ach_prenote',
            'completed': True
        }
        self._add_recipient()
        request = self._make_request(transfers = [achResult])
        response = self._call(request)
        notify_customer.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_recipient_is_distributor(self, notify_customer):
        result = {
            'recipient_id': '10',
            'completed': True
        }
        self._add_recipient()
        request = self._make_request(transfers = [result])
        response = self._call(request)
        notify_customer.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.log.exception')
    def test_exception_no_customer(self, exception):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'completed': True,
            'reason': 'error',
            'sender_id': '12'
        }
        request = self._make_request(transfers = [result])
        response = self._call(request)
        exception.assert_called_with("Error in redemption_notification()")
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    def test_exception_customer(self, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'completed': True,
            'reason': 'error',
            'sender_id': '12'
        }
        recipient = self._add_recipient()
        request = self._make_request(transfers = [result])
        response = self._call(request)
        notify_customer.assert_called_with(request, recipient, 'Oops!', "An attempt to use your Ferly Card was unsuccessful.",
                        channel_id='card-used', data={'type': 'redemption_error', 'reason': 'error'})
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.log.exception')
    def test_exception_no_reason(self, exception):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'completed': True,
            'sender_id': '12'
        }
        self._add_recipient()
        request = self._make_request(transfers = [result])
        response = self._call(request)
        exception.assert_called_with("Error in redemption_notification()")
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.log.exception')
    def test_exception_no_sender_id(self, exception):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'completed': True,
        }
        self._add_recipient()
        request = self._make_request(transfers = [result])
        response = self._call(request)
        exception.assert_called_with("Error in redemption_notification()")
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_not_customer_loopid_not_zero(self, exception, notify_customer):
        result = {
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '1', 'currency': 'USD'}]}],
            'id': '6',
        }
        request = self._make_request(transfers=[result])
        response = self._call(request)
        notify_customer.assert_not_called()
        exception.assert_not_called()
        self.assertEqual(response,{})


    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_no_design_loopid_not_zero(self, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '1', 'currency': 'USD'}]}],
            'id': '6',
        }
        self._add_recipient()
        request = self._make_request(transfers=[result])
        response = self._call(request)
        notify_customer.assert_not_called()
        exception.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_notification_already_sent(self, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '42', 'currency': 'USD'}]}],
            'id': '6',
            'sender_id': '12'
        }
        recipient = self._add_recipient()
        self._add_designs()
        self._add_notification(customer_id=recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        notify_customer.assert_not_called()
        exception.assert_not_called()
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_notification_gift(self, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '42', 'currency': 'USD'}]}],
            'id': '13',
            'sender_id': '12',
            'appdata.ferly.transactionType': 'gift'
        }
        customer = self._add_recipient()
        past_recipient = self._add_recipient(wc_id='13', username='blah')
        self._add_designs()
        self._add_notification(customer_id=past_recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        body = 'You gifted $4.00 Best Buy.'
        notify_customer.assert_called_with(request, customer, 'Gift', body,
                    channel_id='card-used')
        self.assertEqual(response,{})


    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_notification_not_already_sent_card_redemption(self, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '42', 'currency': 'USD'}]}],
            'id': '14',
            'sender_id': '12'
        }
        customer = self._add_recipient()
        past_recipient = self._add_recipient(wc_id='13', username='blah')
        self._add_designs()
        self._add_notification(customer_id=past_recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        body = 'Your Ferly card was used to redeem $4.00 Best Buy.'
        notify_customer.assert_called_with(request, customer, 'Redemption', body, channel_id='card-used')
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    def test_notification_purchase(self, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '4.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '42', 'currency': 'USD'}]}],
            'id': '15',
            'sender_id': '12',
            'appdata.ferly.transactionType': 'purchase'
        }
        customer = self._add_recipient()
        past_recipient = self._add_recipient(wc_id='13', username='blah')
        self._add_designs()
        self._add_notification(customer_id=past_recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        body = 'You purchased $4.00 Best Buy.'
        notify_customer.assert_called_with(request, customer, 'Purchase', body,
                    channel_id='card-used')
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    @patch('backend.appapi.views.app_views.completeTrade')
    @patch('backend.appapi.views.app_views.completeAcceptTrade')
    def test_open_loop_trade_with_rewards(self, completeAcceptTrade, completeTrade, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '20.00',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '0', 'currency': 'USD'}]}],
            'id': '16',
            'sender_id': '12',
        }
        customer = self._add_recipient()
        completeAcceptTrade.return_value = {'transfer': {'id': '3'}}
        completeTrade.return_value = {'transfer': {'id': '3'}}
        past_recipient = self._add_recipient(wc_id='13', username='blah')
        self._add_designs()
        self._add_notification(customer_id=past_recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        body = 'You added $20.00 of Ferly Cash and earned $1.00 Ferly Rewards.'
        notify_customer.assert_called_with(request, customer, 'Added!', body,
                    channel_id='card-used',data={'type': 'add', 'amounts': ['20.00','1.00'],
                            'Titles': ['Ferly Cash', 'Ferly Rewards']})
        self.assertEqual(response,{})

    @patch('backend.appapi.views.app_views.notify_customer')
    @patch('backend.appapi.views.app_views.log.exception')
    @patch('backend.appapi.views.app_views.completeTrade')
    @patch('backend.appapi.views.app_views.completeAcceptTrade')
    def test_open_loop_trade_no_rewards(self, completeAcceptTrade, completeTrade, exception, notify_customer):
        result = {
            'recipient_id': '12',
            'workflow_type': 'test',
            'amount': '0.10',
            'completed': True,
            'movements': [{'loops': [{'loop_id': '0', 'currency': 'USD'}]}],
            'id': '17',
            'sender_id': '12',
        }
        customer = self._add_recipient()
        completeAcceptTrade.return_value = {'transfer': {'id': '3'}}
        completeTrade.return_value = {'transfer': {'id': '3'}}
        past_recipient = self._add_recipient(wc_id='13', username='blah')
        self._add_designs()
        self._add_notification(customer_id=past_recipient.id)
        request = self._make_request(transfers=[result])
        response = self._call(request)
        body = 'You added $0.10 of Ferly Cash.'
        notify_customer.assert_called_with(request, customer, 'Added!', body,
                    channel_id='card-used',data={'type': 'add', 'amounts': ['0.10'],
                            'Titles': ['Ferly Cash']})
        self.assertEqual(response,{})