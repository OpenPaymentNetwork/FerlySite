
from backend.appapi.schemas import customer_views_schemas as schemas
from backend.database.models import Customer
from backend.database.models import Design
from backend.database.models import Device
from backend.testing import DBFixture
from pyramid.httpexceptions import HTTPServiceUnavailable
from unittest import TestCase
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


requests_config = {
    'post.return_value.content':
        "<AddressValidateResponse><Address/></AddressValidateResponse>"
}


@patch('backend.appapi.views.customer_views.get_device')
@patch('backend.appapi.views.customer_views.requests', **requests_config)
class TestRequestCard(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import request_card
        return request_card(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'default_device_id',
            'name': 'default_name',
            'line1': 'default_line1',
            'city': 'default_city',
            'state': 'UT',
            'zip_code': '84062'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        request.ferlysettings = MagicMock()
        request.ferlysettings.usps_address_info_url = (
            'http://production.shippingapis.com/ShippingAPITest.dll')
        request.ferlysettings.usps_username = kw.get(
            'usps_username', 'default_usps_username')
        params.return_value = schemas.AddressSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, requests, get_device):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.AddressSchema))

    def test_no_usps_username_exception(self, requests, get_device):
        request = self._make_request()
        request.ferlysettings.usps_username = None
        with self.assertRaises(Exception) as cm:
            self._call(request)
        self.assertEqual("No USPS username is set", str(cm.exception))

    def test_usps_args(self, requests, get_device):
        usps_request_values = {
            'usps_username': 'my_usps_username',
            'line1': 'my_line1',
            'line2': 'my_line2',
            'city': 'my_city',
            'state': 'AZ',
            'zip_code': '84043'
        }
        usps_request = (
            "API=Verify&XML="
            '<AddressValidateRequest USERID="{usps_username}"><Address ID="0">'
            "<Address1>{line2}</Address1><Address2>{line1}</Address2>"
            "<City>{city}</City><State>{state}</State><Zip5>{zip_code}</Zip5>"
            "<Zip4></Zip4></Address></AddressValidateRequest>").format(
            **usps_request_values)
        self._call(self._make_request(**usps_request_values))
        requests.post.assert_called_once_with(
            'http://production.shippingapis.com/ShippingAPITest.dll',
            data=usps_request, headers={'Content-Type': 'application/xml'})

    def test_malicious_input(self, requests, get_device):
        usps_request_values = {
            'usps_username': 'my_usps_username',
            'line1': '<script>',
            'line2': '&',
            'city': '"\'',
            'state': 'CA',
            'zip_code': '90210'
        }
        escaped_values = {
            'usps_username': 'my_usps_username',
            'line1': '&lt;script&gt;',
            'line2': '&amp;',
            'city': '&#34;&#39;',
            'state': 'CA',
            'zip_code': '90210'
        }
        usps_request = (
            "API=Verify&XML="
            '<AddressValidateRequest USERID="{usps_username}"><Address ID="0">'
            "<Address1>{line2}</Address1><Address2>{line1}</Address2>"
            "<City>{city}</City><State>{state}</State><Zip5>{zip_code}</Zip5>"
            "<Zip4></Zip4></Address></AddressValidateRequest>").format(
            **escaped_values)
        self._call(self._make_request(**usps_request_values))
        requests.post.assert_called_once_with(
            'http://production.shippingapis.com/ShippingAPITest.dll',
            data=usps_request, headers={'Content-Type': 'application/xml'})

    def test_usps_connection_fails(self, requests, get_device):
        requests.post.return_value.raise_for_status.side_effect = Exception
        with self.assertRaises(HTTPServiceUnavailable):
            self._call(self._make_request())

    def test_usps_request_error(self, requests, get_device):
        requests.post.return_value.content = "<Error/>"
        with self.assertRaises(HTTPServiceUnavailable):
            self._call(self._make_request())

    def test_address_error(self, requests, get_device):
        requests.post.return_value.content = (
            "<AddressValidateResponse><Address><Error>"
            "<Description>There was an address error.</Description>"
            "</Error></Address></AddressValidateResponse>")
        response = self._call(self._make_request())
        expected_response = {
            'error': 'invalid_address',
            'description': 'There was an address error.'
        }
        self.assertEqual(response, expected_response)

    @patch('backend.appapi.views.customer_views.CardRequest')
    def test_card_request_added(self, CardRequest, requests, get_device):
        address_values = {
            'line1': 'my_line1',
            'line2': 'my_line2',
            'city': 'my_city',
            'state': 'TX',
        }
        requests.post.return_value.content = (
            "<AddressValidateResponse><Address>"
            "<Address1>{line2}</Address1><Address2>{line1}</Address2>"
            "<City>{city}</City><State>{state}</State>"
            "<Zip5>84606</Zip5><Zip4>3709</Zip4>"
            "</Address></AddressValidateResponse>").format(**address_values)
        request = self._make_request(
            line1='original_line1',
            line2='original_line2',
            state='CA',
            city='original_city',
            zip_code='84047',
            name='my_name'
        )
        self._call(request)
        CardRequest.assert_called_once_with(
            customer_id=get_device.return_value.customer.id,
            original_line1='original_line1',
            original_line2='original_line2',
            original_city='original_city',
            original_state='CA',
            original_zip_code='84047',
            name='my_name',
            zip_code='84606-3709',
            **address_values
        )
        request.dbsession.add.assert_called_once_with(CardRequest.return_value)

    def test_return_values(self, requests, get_device):
        address_values = {
            'line1': 'my_line1',
            'line2': 'my_line2',
            'city': 'my_city',
            'state': 'AZ'
        }
        requests.post.return_value.content = (
            "<AddressValidateResponse><Address>"
            "<Address1>{line2}</Address1><Address2>{line1}</Address2>"
            "<City>{city}</City><State>{state}</State>"
            "<Zip5>84606</Zip5><Zip4>3709</Zip4>"
            "</Address></AddressValidateResponse>").format(**address_values)
        response = self._call(self._make_request(name='my_name'))
        address_values.update({'name': 'my_name', 'zip_code': '84606-3709'})
        self.assertEqual(response, address_values)


class TestSignUp(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import signup
        return signup(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername',
            'expo_token:': 'defaulttoken',
            'os': 'defaultos:android'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.RegisterSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.RegisterSchema))

    def test_already_registered(self):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mdevice = MagicMock()
        mock_query.filter.return_value.first.return_value = mdevice
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_query(self):
        device_id = '123'
        request = self._make_request(device_id=device_id)
        mock_query = request.dbsession.query = MagicMock()
        mock_filter = mock_query.return_value.filter = MagicMock()
        self._call(request)
        expression = Device.device_id == device_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.appapi.views.customer_views.Device')
    @patch('backend.appapi.views.customer_views.Customer')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_add_customer(self, mock_wc_contact, customer, mock_device):
        first_name = 'firstname'
        last_name = 'lastname'
        username = 'username'
        request = self._make_request(
            first_name=first_name, last_name=last_name, username=username)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        wc_id = 'newid'
        mock_wc_contact.return_value.json.return_value = {'id': wc_id}
        customer.return_value.id = 'customerid'
        mock_customer = {'wc_id': wc_id, 'first_name': first_name,
                         'username': username, 'last_name': last_name}
        self._call(request)
        customer.assert_called_once_with(**mock_customer)
        request.dbsession.add.assert_any_call(customer.return_value)

    @patch('backend.appapi.views.customer_views.Device')
    @patch('backend.appapi.views.customer_views.Customer')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_add_device(self, mock_wc_contact, customer, mock_device):
        device_id = 'deviceid'
        os = 'android:28'
        expo_token = 'myexpotoken'
        request = self._make_request(
            device_id=device_id, os=os, expo_token=expo_token)
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        customer.return_value.id = customer_id = 'customerid'
        device = {'device_id': device_id, 'customer_id': customer_id, 'os': os,
                  'expo_token': expo_token}
        self._call(request)
        mock_device.assert_called_once_with(**device)
        request.dbsession.add.assert_any_call(mock_device.return_value)

    @patch('backend.appapi.views.customer_views.Device')
    @patch('backend.appapi.views.customer_views.Customer')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_db_flush(self, mock_wc_contact, customer, mock_device):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        mdevice = mock_device.return_value
        self._call(request)
        request.dbsession.assert_has_calls(
            [call.add(customer.return_value), call.flush, call.add(mdevice)])

    @patch('backend.appapi.views.customer_views.Device')
    @patch('backend.appapi.views.customer_views.Customer')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_update_tsvector(self, mock_wc_contact, customer, mock_device):
        request = self._make_request()
        mock_query = request.dbsession.query.return_value
        mock_query.filter.return_value.first.return_value = None
        self._call(request)
        customer.return_value.update_tsvector.assert_called()

    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_wc_contact_params(self, mock_wc_contact):
        first_name = 'firstname'
        last_name = 'lastname'
        request = self._make_request(
            first_name=first_name, last_name=last_name)
        mock_query = request.dbsession.query.return_value
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

    def test_deny_existing_username(self):
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.side_effect = [None, not None]
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})


class TestEditProfile(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import edit_profile
        return edit_profile(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.EditProfileSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.EditProfileSchema))

    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_unchanged_username(self, get_device, get_token, wc_contact):
        request = self._make_request()
        customer = get_device.return_value.customer
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = customer
        response = self._call(request)
        self.assertEqual(response, {})

    @patch('backend.appapi.views.customer_views.get_device')
    def test_existing_username(self, get_device):
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = not None
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_edit_username_only(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        customer.first_name = current_first_name = 'firstname'
        customer.last_name = current_last_name = 'lastname'
        customer.username = 'current_username'
        newusername = 'newusername'
        request = self._make_request(
            first_name=current_first_name,
            last_name=current_last_name,
            username=newusername
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        self.assertFalse(get_wc_token.called)
        self.assertFalse(wc_contact.called)
        self.assertEqual(customer.first_name, current_first_name)
        self.assertEqual(customer.last_name, current_last_name)
        self.assertEqual(customer.username, newusername)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_edit_first_name_only(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        customer.first_name = 'firstname'
        customer.last_name = current_last_name = 'lastname'
        customer.username = current_username = 'username'
        new_first_name = 'new_first_name'
        request = self._make_request(
            first_name=new_first_name,
            last_name=current_last_name,
            username=current_username
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, customer)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': new_first_name,
                'last_name': current_last_name
            })
        self.assertEqual(customer.first_name, new_first_name)
        self.assertEqual(customer.last_name, current_last_name)
        self.assertEqual(customer.username, current_username)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_edit_last_name_only(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        customer.first_name = current_first_name = 'firstname'
        customer.last_name = 'lastname'
        customer.username = current_username = 'username'
        new_last_name = 'new_first_name'
        request = self._make_request(
            first_name=current_first_name,
            last_name=new_last_name,
            username=current_username
        )
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        get_wc_token.assert_called_with(request, customer)
        wc_contact.assert_called_with(
            request,
            'POST',
            'wallet/change-name',
            access_token=get_wc_token.return_value,
            params={
                'first_name': current_first_name,
                'last_name': new_last_name
            })
        self.assertEqual(customer.first_name, current_first_name)
        self.assertEqual(customer.last_name, new_last_name)
        self.assertEqual(customer.username, current_username)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_update_tsvector(self, get_device, wc_contact, get_wc_token):
        customer = get_device.return_value.customer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        self._call(request)
        customer.update_tsvector.assert_called()


class TestIsCustomer(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import is_customer
        return is_customer(*args, **kw)

    def _make_request(self, **args):
        request_params = {
            'device_id': args.get('device_id', 'defaultdevice'),
            'expected_env': args.get('expected_env', 'staging')
        }
        request = pyramid.testing.DummyRequest(params=request_params)
        settings = request.ferlysettings = MagicMock()
        settings.environment = args.get('environment', 'staging')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.IsCustomerSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _add_device(self):
        from backend.database.models import Customer, Device
        dbsession = self.dbsession
        customer = Customer(
            wc_id='11',
            first_name='Testy',
            last_name='Customer',
            username='testycust',
        )
        dbsession.add(customer)
        dbsession.flush()  # Assign customer.id

        device = Device(
            device_id='defaultdevice',
            customer_id=customer.id,
        )
        dbsession.add(device)
        dbsession.flush()  # Assign device.id

        return device

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.IsCustomerSchema))

    def test_expected_env_mismatch(self):
        response = self._call(self._make_request(environment='production'))
        self.assertEqual(response, {'error': 'unexpected_environment'})

    def test_invalid_device_id(self):
        request = self._make_request()
        response = self._call(request)
        self.assertFalse(response.get('is_customer'))

    def test_valid_device_id(self):
        self._add_device()
        response = self._call(self._make_request())
        self.assertTrue(response.get('is_customer'))

    def test_dont_find_wrong_device(self):
        self._add_device()
        request = self._make_request(device_id='123')
        response = self._call(request)
        self.assertFalse(response.get('is_customer'))


class TestSend(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import send
        return send(*args, **kw)

    def _make_request(self, **args):
        request_params = {
            'expected_env': args.get('expected_env', 'staging'),
            'device_id': args.get('device_id', 'defaultdevice'),
            'recipient_id': args.get('recipient_id', '01'),
            'amount': '2.53',
            'design_id': args.get('design_id', '00'),
        }
        message = args.get('message')
        if message:
            request_params['message'] = message
        request = pyramid.testing.DummyRequest()
        settings = request.ferlysettings = MagicMock()
        settings.environment = args.get('environment', 'staging')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.SendSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _add_device(self, recipient_id='recip'):
        from backend.database.models import Customer, Device
        dbsession = self.dbsession
        self.customer = customer = Customer(
            wc_id='11',
            first_name='Testy',
            last_name='Customer',
            username='testycust',
        )
        dbsession.add(customer)
        dbsession.flush()  # Assign customer.id

        device = Device(
            device_id='defaultdevice',
            customer_id=customer.id,
        )
        dbsession.add(device)
        dbsession.flush()  # Assign device.id

        return device

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

    def _add_recipient(self):
        from backend.database.models import Customer
        dbsession = self.dbsession
        recipient = Customer(
            wc_id='12',
            first_name='Friend',
            last_name='User',
            username='friend',
        )
        dbsession.add(recipient)
        dbsession.flush()  # Assign recipient.id
        return recipient

    def test_correct_schema_used(self):
        self._add_device()
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.SendSchema))

    def test_invalid_design(self):
        self._add_device()
        request = self._make_request()
        response = self._call(request)
        self.assertEqual({'error': 'invalid_design'}, response)

    @patch('backend.appapi.views.customer_views.notify_customer')
    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_success_without_message(
            self, wc_contact, get_wc_token, notify_customer):
        self._add_device()
        design = self._add_design()
        recipient = self._add_recipient()
        self.customer.recents = [
            'cust1', 'cust2', 'cust3', 'cust4', recipient.id,
            'cust5', 'cust6', 'cust7', 'cust8', 'cust9']

        request = self._make_request(
            design_id=design.id, recipient_id=recipient.id)
        response = self._call(request)
        self.assertEqual({}, response)

        access_token = get_wc_token.return_value
        get_wc_token.assert_called_with(request, self.customer)
        expect_params = {
            'sender_id': '11',
            'recipient_uid': 'wingcash:12',
            'amounts': '41-USD-2.53',
            'require_recipient_email': False,
            'accepted_policy': True,
        }
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/send', params=expect_params,
            access_token=access_token)

        notify_customer.assert_called_with(
            request,
            recipient,
            'Received $2.53 Test Design',
            'from Testy Customer',
            channel_id='gift-received')

        self.assertEqual([
            recipient.id, 'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8'], self.customer.recents)

    @patch('backend.appapi.views.customer_views.notify_customer')
    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_with_message(self, wc_contact, get_wc_token, notify_customer):
        self._add_device()
        design = self._add_design()
        recipient = self._add_recipient()
        self.customer.recents = [
            'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8']

        request = self._make_request(
            design_id=design.id, recipient_id=recipient.id, message='hi sir')
        response = self._call(request)
        self.assertEqual({}, response)

        access_token = get_wc_token.return_value
        get_wc_token.assert_called_with(request, self.customer)
        expect_params = {
            'sender_id': '11',
            'recipient_uid': 'wingcash:12',
            'amounts': '41-USD-2.53',
            'require_recipient_email': False,
            'accepted_policy': True,
            'message': 'hi sir',
        }
        wc_contact.assert_called_with(
            request, 'POST', 'wallet/send', params=expect_params,
            access_token=access_token)

        notify_customer.assert_called_with(
            request,
            recipient,
            'Received $2.53 Test Design',
            'hi sir\nfrom Testy Customer',
            channel_id='gift-received')

        self.assertEqual([
            recipient.id, 'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8'], self.customer.recents)


class TestHistory(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import history
        return history(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.HistorySchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_transfer(self, **kw):
        loop_id = kw.pop('loop_id', 'defaultloopid')
        sender_title = kw.pop('sender_title', 'defaultsendertitle')
        sender_is_individual = kw.pop('sender_is_individual', True)
        recipient_title = kw.pop('recipient_title', 'defaultrecipienttitle')
        recipient_is_individual = kw.pop('recipient_is_individual', True)
        transfer = {
            'amount': 0,
            'timestamp': 'timestamp',
            'movements': [{'loops': [{'loop_id': loop_id}]}],
            'sender_info': {
                'title': sender_title, 'is_individual': sender_is_individual},
            'recipient_info': {
                'title': recipient_title,
                'is_individual': recipient_is_individual
            },
            'recipient_id': 'defaultrecipientid',
            'sender_id': 'defaultsenderid',
            'id': 'defaultid'
        }
        transfer.update(**kw)
        return transfer

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.HistorySchema))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_get_wc_contact_args(self, get_device, wc_contact, get_wc_token):
        limit = 100
        offset = 0
        customer = get_device.return_value.customer
        access_token = get_wc_token.return_value
        request = self._make_request(limit=limit, offset=offset)
        post_params = {'limit': limit, 'offset': offset}
        self._call(request)
        get_device.assert_called()
        get_wc_token.assert_called_with(request, customer)
        wc_contact.assert_called_with(
            request, 'GET', 'wallet/history', params=post_params,
            access_token=access_token)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_has_more_is_returned(self, wc_contact, get_wc_token):
        more = True
        wc_contact.return_value.json.return_value = {'more': more}
        response = self._call(self._make_request())
        self.assertEqual(more, response['has_more'])

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_design_query(self, wc_contact, get_wc_token):
        loop_id = 'myloop_id'
        results = [self._make_transfer(loop_id=loop_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Design.wc_id == loop_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_design_title_is_returned(self, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_design = mock_filter.return_value.first.return_value
        mock_design.title = 'ftitle'
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_title'], 'ftitle')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_design_logo_image_url_is_returned(self, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_design = mock_filter.return_value.first.return_value
        mock_design.logo_image_url = 'mylogourl'
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_logo_image_url'], 'mylogourl')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_amount_is_returned(self, wc_contact, get_wc_token):
        amount = 10
        request = self._make_request()
        results = [self._make_transfer(amount=amount)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['amount'], amount)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_timestamp_is_returned(self, wc_contact, get_wc_token):
        import datetime
        timestamp = datetime.datetime.utcnow()
        request = self._make_request()
        results = [self._make_transfer(timestamp=timestamp)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['timestamp'], timestamp)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_id_is_returned(self, wc_contact, get_wc_token):
        transfer_id = 'mytransfer_id'
        request = self._make_request()
        results = [self._make_transfer(id=transfer_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['id'], transfer_id)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_multiple_results(self, wc_contact, get_wc_token):
        request = self._make_request()
        transfer = self._make_transfer()
        results = [transfer, transfer, transfer]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        self.assertEqual(len(response['history']), len(results))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_sender_counter_party(self, get_device, wc_contact, get_wc_token):
        customer_wc_id = 'mycustomerid'
        recipient_title = 'myrecipient_title'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=customer_wc_id, recipient_title=recipient_title)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = customer_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['counter_party'], recipient_title)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_recipient_counter_party(
            self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'mycustomerid'
        sender_title = 'mysender_title'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_title=sender_title)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['counter_party'], sender_title)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_redeem_type(self, get_device, wc_contact, get_wc_token):
        sender_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=sender_wc_id, recipient_is_individual=False)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = sender_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'redeem')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_send_type(self, get_device, wc_contact, get_wc_token):
        sender_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            sender_id=sender_wc_id, recipient_is_individual=True)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = sender_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'send')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_receive_type(self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_is_individual=True)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'receive')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_purchase_type(self, get_device, wc_contact, get_wc_token):
        recipient_wc_id = 'mywcid'
        request = self._make_request()
        results = [self._make_transfer(
            recipient_id=recipient_wc_id, sender_is_individual=False)]
        wc_contact.return_value.json.return_value = {'results': results}
        customer = get_device.return_value.customer
        customer.wc_id = recipient_wc_id
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'purchase')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_unrecognized_design(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_filter.return_value.first.return_value = None
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_title'], 'Unrecognized')
        self.assertEqual(transfer['design_logo_image_url'], '')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_unrecognized_customer_role(
            self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        mock_filter = request.dbsession.query.return_value.filter
        mock_filter.return_value.first.return_value = None
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'unrecognized')


class TestTransfer(TestCase):

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import transfer
        return transfer(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'device_id': 'defaultdeviceid',
            'transfer_id': 'defaulttransferid'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.TransferSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_transfer(self, **kw):
        sender_id = kw.pop('sender_id', 'defaultsenderid')
        recipient_id = kw.pop('recipient_id', 'defaultrecipientid')
        sender_is_individual = kw.pop('sender_is_individual', True)
        recipient_is_individual = kw.pop('recipient_is_individual', True)
        transfer = {
            'sender_info': {
                'uid_value': sender_id,
                'is_individual': sender_is_individual
            },
            'recipient_info': {
                'uid_value': recipient_id,
                'is_individual': recipient_is_individual
            },
            'recipient_id': recipient_id,
            'sender_id': sender_id,
            'message': 'defaultmessage'
        }
        transfer.update(**kw)
        return transfer

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    def test_correct_schema_used(self, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.TransferSchema))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_get_wc_contact_args(self, get_device, wc_contact, get_wc_token):
        transfer_id = 'mytransferid'
        customer = get_device.return_value.customer
        access_token = get_wc_token.return_value
        request = self._make_request(transfer_id=transfer_id)
        self._call(request)
        get_device.assert_called()
        get_wc_token.assert_called_with(request, customer)
        wc_contact.assert_called_with(
            request, 'GET', 't/{0}'.format(transfer_id),
            access_token=access_token)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_message_is_returned(self, get_device, wc_contact, get_wc_token):
        message = 'mymessage'
        customer_id = 'mycustomerid'
        customer = get_device.return_value.customer
        customer.wc_id = customer_id
        transfer = self._make_transfer(sender_id=customer_id, message=message)
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response['message'], message)

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_sender_counter_party(self, get_device, wc_contact, get_wc_token):
        recipient_id = 'myrecipientid'
        sender_id = 'mysenderid'
        customer = get_device.return_value.customer
        customer.wc_id = recipient_id
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Customer.wc_id == sender_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_recipient_counter_party(
            self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        recipient_id = 'myrecipientid'
        customer = get_device.return_value.customer
        customer.wc_id = sender_id
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Customer.wc_id == recipient_id
        self.assertTrue(expression.compare(mock_filter.call_args[0][0]))

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_permission_denied(self, get_device, wc_contact, get_wc_token):
        recipient_id = 'myrecipientid'
        sender_id = 'mysenderid'
        customer = get_device.return_value.customer
        customer.wc_id = 'differentid'
        transfer = self._make_transfer(
            recipient_id=recipient_id, sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'permission_denied'})

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_query_for_customers_only(
            self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        customer = get_device.return_value.customer
        customer.wc_id = sender_id
        transfer = self._make_transfer(
            sender_id=sender_id, recipient_is_individual=False)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        self._call(request)
        request.dbsession.query.assert_not_called()

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_no_counter_party_customer(
            self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        customer = get_device.return_value.customer
        customer.wc_id = sender_id
        transfer = self._make_transfer(sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value = None
        response = self._call(request)
        self.assertEqual(response['counter_party_profile_image_url'], '')

    @patch('backend.appapi.views.customer_views.get_wc_token')
    @patch('backend.appapi.views.customer_views.wc_contact')
    @patch('backend.appapi.views.customer_views.get_device')
    def test_profile_image_url_is_returned(
            self, get_device, wc_contact, get_wc_token):
        sender_id = 'mysenderid'
        customer = get_device.return_value.customer
        customer.wc_id = sender_id
        transfer = self._make_transfer(sender_id=sender_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        image_url = 'myimageurl'
        mock_filter = request.dbsession.query.return_value.filter.return_value
        mock_filter.first.return_value.profile_image_url = image_url
        response = self._call(request)
        self.assertEqual(
            response['counter_party_profile_image_url'], image_url)
