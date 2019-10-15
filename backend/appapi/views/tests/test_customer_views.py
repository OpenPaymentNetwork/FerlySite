
from backend.appapi.schemas import customer_views_schemas as schemas
from backend.database.models import Design
from backend.database.models import Device
from backend import settings
from backend.testing import add_device
from backend.testing import DBFixture
from pyramid.httpexceptions import HTTPServiceUnavailable
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing
import uuid


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


@patch('backend.appapi.views.customer_views.get_device')
@patch('backend.appapi.views.customer_views.requests', **{
    'post.return_value.content':
        "<AddressValidateResponse><Address/></AddressValidateResponse>"
})
class TestRequestCard(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import request_card
        return request_card(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'name': 'default_name',
            'line1': 'default_line1',
            'city': 'default_city',
            'state': 'UT',
            'zip_code': '84062',
            'verified': 'yes'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.dbsession = self.dbsession
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
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.AddressSchema))

    def test_get_device_called(self, requests, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called()

    def test_no_usps_username_exception(self, requests, get_device):
        request = self._make_request()
        request.ferlysettings.usps_username = None
        with self.assertRaises(Exception) as cm:
            self._call(request)
        self.assertEqual("No USPS username is set", str(cm.exception))

    def test_usps_args(self, requests, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
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
        get_device.return_value = add_device(self.dbsession)[0]
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

    def test_card_request_added(self, requests, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
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
        from backend.database.models import CardRequest
        cr = self.dbsession.query(CardRequest).one()

        self.assertEqual(get_device.return_value.customer.id, cr.customer_id)
        self.assertEqual('original_line1', cr.original_line1)
        self.assertEqual('original_line2', cr.original_line2)
        self.assertEqual('original_city', cr.original_city)
        self.assertEqual('CA', cr.original_state)
        self.assertEqual('84047', cr.original_zip_code)
        self.assertEqual('my_name', cr.name)
        self.assertEqual('84606-3709', cr.zip_code)
        self.assertEqual('my_line1', cr.line1)
        self.assertEqual('my_line2', cr.line2)
        self.assertEqual('my_city', cr.city)
        self.assertEqual('TX', cr.state)

    def test_return_values(self, requests, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
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


@patch('backend.appapi.views.customer_views.wc_contact')
class Test_add_individual(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import add_individual
        return add_individual(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername',
            'profile_id': 'myprofileid',
            'expo_token': 'defaulttoken',
            'os': 'defaultos:android'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.ferlysettings = MagicMock()
        request.ferlysettings.wingcash_client_id = kw.get('WINGCASH_CLIENT_ID', '123456789')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.RegisterSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_response(self, json_content):
        class MockJSONResponse:
            def json(self):
                return json_content

        return MockJSONResponse()

    def test_correct_schema_used(self, wc_contact):
        wc_contact.return_value = self._make_response({'id': '12345678901'})
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.RegisterSchema))

    def test_already_registered(self, wc_contact):
        add_device(self.dbsession)
        request = self._make_request()
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_add_customer_and_device(self, wc_contact):
        wc_contact.return_value = self._make_response({'id': '12345678901'})
        request = self._make_request()
        self._call(request)
        devices = self.dbsession.query(Device).all()
        self.assertEqual(1, len(devices))
        customer = devices[0].customer
        self.assertEqual('defaultfirstname', customer.first_name)
        self.assertEqual('defaultlastname', customer.last_name)
        self.assertEqual('defaultusername', customer.username)
        self.assertEqual('12345678901', customer.wc_id)
        self.assertEqual('defaulttoken', devices[0].expo_token)
        self.assertEqual('defaultos:android', devices[0].os)
        self.assertEqual(
            "'defaultfirstnam':1 'defaultlastnam':2 'defaultusernam':3",
            customer.tsvector)

    def test_wc_contact_params(self, wc_contact):
        wc_contact.return_value = self._make_response({'id': '12345678901'})
        first_name = 'firstname'
        last_name = 'lastname'
        request = self._make_request(
            first_name=first_name, last_name=last_name)
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
        wc_contact.assert_called_once_with(*args, **kw)

    def test_deny_existing_username(self, wc_contact):
        add_device(self.dbsession)
        request = self._make_request(username='defaultusername')
        request.headers = {
            'Authorization': 'Bearer otherotherotherotherotherotherotherother',
        }
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})


@patch('backend.appapi.views.customer_views.wc_contact')
@patch('backend.appapi.views.customer_views.get_device')
class Test_Signup(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import signup
        return signup(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'login': 'test@test.com',
            'username': 'defaultusername',
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.ferlysettings = MagicMock()
        request.ferlysettings.wingcash_client_id = kw.get('WINGCASH_CLIENT_ID', '123456789')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.SignupSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_response(self, json_content):
        class MockJSONResponse:
            def json(self):
                return json_content

        return MockJSONResponse()

    def test_correct_schema_used(self, get_device, wc_contact):
        wc_contact.return_value = self._make_response({
            "attempt_path":"/aa/5618911532/",
            "captcha_required": False,
            "code_length":9,
            "factor_id":"fb546e07",
            "revealed_codes": ["073467126 => email:ex3@example.com"],
            "secret":"q9ieEMNt0G3RbgTBjlOWy5C7vhY",
            "trust30":False,
            "unauthenticated": {
                "email:ex3@example.com": {
                    "country":None,
                    "original":"ex3@example.com"
                }
            }
        })
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.SignupSchema))

    def test_already_registered(self, get_device, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        response = self._call(request)
        expected_response = {'error': 'device_already_registered'}
        self.assertEqual(response, expected_response)

    def test_deny_existing_username(self, get_device, wc_contact):
        add_device(self.dbsession)
        request = self._make_request(username='defaultusername')
        request.headers = {
            'Authorization': 'Bearer otherotherotherotherotherotherotherother',
        }
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

@patch('backend.appapi.views.customer_views.wc_contact')
class Test_set_signup_data(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import set_signup_data
        return set_signup_data(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'attempt_path': 'aa/123456789/',
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'secret': 'secret',
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.ferlysettings = MagicMock()
        request.ferlysettings.wingcash_client_id = kw.get('WINGCASH_CLIENT_ID', '123456789')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.SetSignupDataSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_response(self, json_content):
        class MockJSONResponse:
            def json(self):
                return json_content

        return MockJSONResponse()

    def test_correct_schema_used(self, wc_contact):
        wc_contact.return_value = self._make_response({
            "authenticated":{
                "email:ex3@example.com":{
                    "country":None,
                    "original":"ex3@example.com",
                    "strong":False,
                    "used_password":False
                },
            },
            "captcha_required":False,
            "completed_mfa":True,
            "invite_id":None,
            "profile_id":None,
            "profile_title":None,
            "signup":{
                "first_name":"Jacques",
                "has_password":False,
                "last_name":"Black",
                "name_checked":True
            },"trust30":False
        })
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.SetSignupDataSchema))

@patch('backend.appapi.views.customer_views.wc_contact')
class Test_set_signup_finish(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import signup_finish
        return signup_finish(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'agreed': True,
            'attempt_path': 'aa/123456789/',
            'secret': 'secret',
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        request.ferlysettings = MagicMock()
        request.ferlysettings.wingcash_client_id = kw.get('WINGCASH_CLIENT_ID', '123456789')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.SignupFinishSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _make_response(self, json_content):
        class MockJSONResponse:
            def json(self):
                return json_content

        return MockJSONResponse()

    def test_correct_schema_used(self, wc_contact):
        wc_contact.return_value = self._make_response({
            "authenticated":{
                "email:ex3@example.com":{
                    "country":None,
                    "original":"ex3@example.com",
                    "strong":False,
                    "used_password":False
                },
            },
            "captcha_required":False,
            "completed_mfa":True,
            "invite_id":None,
            "profile":{
                "accepted_national_currencies":[],
                "address":"",
                "address_data":None,
                "chain_id":None,
                "first_name":"Jacques",
                "id":"4356518574",
                "image125":None,
                "image24":None,
                "image25":None,
                "image250w":None,
                "image48":None,
                "image50":None,
                "image73":None,
                "is_individual":True,
                "last_name":"Black",
                "latitude":"",
                "longitude":"",
                "phone":"",
                "preferred_currency":"",
                "support_paycode":False,
                "title":"Jacques Black",
                "unsupported_national_currencies":[],
                "url":"https://wingcash.com/p/4356518574/",
                "username":None,
                "wingcash_uid":"wingcash:4356518574"
            },
            "profile_id":"4356518574",
            "profile_title":"Jacques Black",
            "signup":{
                "first_name":"Jacques",
                "has_password":False,
                "last_name":"Black",
                "name_checked":True
            },
            "token":{
                "access_token":"t4954253560-7284763818-kaW6ppOwOHcKZ-Q-25GPneef2Mk",
                "expires_in":899,
                "hard_expires_in":316223999,
                "scope":"accept_offer change_settings edit_account list_friends manage_account manage_sent mobile_device send_cash send_to_account view view_full_history view_history view_wallet",
                "token_type":"bearer"
            },
            "trust30":False
        })
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.SignupFinishSchema))

@patch('backend.appapi.views.customer_views.wc_contact')
@patch('backend.appapi.views.customer_views.get_wc_token')
@patch('backend.appapi.views.customer_views.get_device')
class TestEditProfile(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import edit_profile
        return edit_profile(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'first_name': 'defaultfirstname',
            'last_name': 'defaultlastname',
            'username': 'defaultusername'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.get_params = params = MagicMock()
        request.dbsession = self.dbsession
        params.return_value = schemas.EditProfileSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self, get_device, get_wc_token, wc_contact):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.EditProfileSchema))

    def test_get_device_called(self, get_device, *args):
        request = self._make_request()
        self._call(request)
        get_device.assert_called()

    def test_unchanged_username(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(response, {})
        wc_contact.assert_not_called()

    def test_existing_username(self, get_device, get_wc_token, wc_contact):
        add_device(
            self.dbsession,
            username='greatusername',
            wc_id='12',
            password=b'otherpassword')
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request(username='greatusername')
        response = self._call(request)
        self.assertEqual(response, {'error': 'existing_username'})

    def test_edit_username_only(self, get_device, get_wc_token, wc_contact):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        customer = device.customer
        customer.first_name = current_first_name = 'firstname'
        customer.last_name = current_last_name = 'lastname'
        customer.username = 'current_username'
        newusername = 'newusername'
        request = self._make_request(
            first_name=current_first_name,
            last_name=current_last_name,
            username=newusername,
        )
        self._call(request)
        self.assertFalse(get_wc_token.called)
        self.assertFalse(wc_contact.called)
        self.assertEqual(customer.first_name, current_first_name)
        self.assertEqual(customer.last_name, current_last_name)
        self.assertEqual(customer.username, newusername)

    def test_edit_first_name_only(self, get_device, get_wc_token, wc_contact):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        customer = device.customer
        customer.first_name = 'firstname'
        customer.last_name = current_last_name = 'lastname'
        customer.username = current_username = 'username'
        new_first_name = 'new_first_name'
        request = self._make_request(
            first_name=new_first_name,
            last_name=current_last_name,
            username=current_username,
        )
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

    def test_edit_last_name_only(self, get_device, get_wc_token, wc_contact):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        customer = device.customer
        customer.first_name = current_first_name = 'firstname'
        customer.last_name = 'lastname'
        customer.username = current_username = 'username'
        new_last_name = 'new_first_name'
        request = self._make_request(
            first_name=current_first_name,
            last_name=new_last_name,
            username=current_username
        )
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

    def test_update_tsvector(self, get_device, get_wc_token, wc_contact):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        customer = device.customer
        customer.update_tsvector = MagicMock()
        request = self._make_request()
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

    def _make_request(self, **kw):
        request_params = {
            'expected_env': 'staging',
        }
        request_params.update(kw)
        request = pyramid.testing.DummyRequest(params=request_params, headers={
            'Authorization': 'Bearer defaultpassword0defaultpassword0',
        })
        settings = request.ferlysettings = MagicMock()
        settings.environment = kw.get('environment', 'staging')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.IsCustomerSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.IsCustomerSchema))

    def test_expected_env_mismatch(self):
        response = self._call(self._make_request(environment='production'))
        self.assertEqual(response, {'error': 'unexpected_environment'})

    def test_invalid_password(self):
        request = self._make_request()
        response = self._call(request)
        self.assertFalse(response.get('is_customer'))

    def test_valid_password(self):
        add_device(self.dbsession)
        response = self._call(self._make_request())
        self.assertTrue(response.get('is_customer'))

    def test_dont_find_wrong_device(self):
        add_device(self.dbsession)
        request = self._make_request()
        request.headers = {
            'Authorization': 'Bearer 12341234123412341234123412341234',
        }
        response = self._call(request)
        self.assertFalse(response.get('is_customer'))


@patch('backend.appapi.views.customer_views.notify_customer')
@patch('backend.appapi.views.customer_views.get_wc_token')
@patch('backend.appapi.views.customer_views.wc_contact')
@patch('backend.appapi.views.customer_views.get_device')
class TestSend(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import send
        return send(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'expected_env': 'staging',
            'recipient_id': '01',
            'amount': '2.53',
            'design_id': '00',
        }
        request_params.update(kw)
        request = pyramid.testing.DummyRequest()
        settings = request.ferlysettings = MagicMock()
        settings.environment = kw.get('environment', 'staging')
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.SendSchema().bind(
            request=request).deserialize(request_params)
        return request

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

    def test_correct_schema_used(self, *args):
        add_device(self.dbsession)
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.SendSchema))

    def test_get_device_called(self, get_device, *args):
        request = self._make_request()
        self._call(request)
        get_device.assert_called()

    def test_invalid_design(self, *args):
        request = self._make_request()
        response = self._call(request)
        self.assertEqual({'error': 'invalid_design'}, response)

    def test_success_without_message(
            self, get_device, wc_contact, get_wc_token, notify_customer):
        device = add_device(self.dbsession)[0]
        customer = device.customer
        get_device.return_value = device

        design = self._add_design()
        recipient = self._add_recipient()
        customer.recents = [
            'cust1', 'cust2', 'cust3', 'cust4', recipient.id,
            'cust5', 'cust6', 'cust7', 'cust8', 'cust9']

        request = self._make_request(
            design_id=design.id, recipient_id=recipient.id)
        response = self._call(request)
        self.assertEqual({}, response)

        access_token = get_wc_token.return_value
        get_wc_token.assert_called_with(request, customer)
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
            'from defaultfirstname defaultlastname',
            channel_id='gift-received')

        self.assertEqual([
            recipient.id, 'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8'], customer.recents)

    def test_with_message(
            self, get_device, wc_contact, get_wc_token, notify_customer):
        device = add_device(self.dbsession)[0]
        customer = device.customer
        get_device.return_value = device

        design = self._add_design()
        recipient = self._add_recipient()
        customer.recents = [
            'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8']

        request = self._make_request(
            design_id=design.id, recipient_id=recipient.id, message='hi sir')
        response = self._call(request)
        self.assertEqual({}, response)

        access_token = get_wc_token.return_value
        get_wc_token.assert_called_with(request, customer)
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
            'hi sir\nfrom defaultfirstname defaultlastname',
            channel_id='gift-received')

        self.assertEqual([
            recipient.id, 'cust1', 'cust2', 'cust3', 'cust4',
            'cust5', 'cust6', 'cust7', 'cust8'], customer.recents)


@patch('backend.appapi.views.customer_views.get_wc_token')
@patch('backend.appapi.views.customer_views.wc_contact')
@patch('backend.appapi.views.customer_views.get_device')
class TestHistory(TestCase):
    maxDiff = None

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import history
        return history(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'password': 'defaultpassword0defaultpassword0'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
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

    def _add_design(
            self,
            loop_id='defaultloopid',
            logo_image_url='mylogourl'):
        dbsession = self.dbsession
        design = Design(
            distribution_id='00101',
            wc_id=loop_id,
            title='ftitle',
            listable=True,
            logo_image_url=logo_image_url,
            wallet_image_url='',
            fee=2,
            field_color='ff9900',
            field_dark=True,
        )
        dbsession.add(design)
        dbsession.flush()  # Assign design.id
        return design

    def test_correct_schema_used(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.HistorySchema))

    def test_get_device_called(self, get_device, *args):
        request = self._make_request()
        self._call(request)
        get_device.assert_called()

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

    def test_has_more_is_returned(self, get_device, wc_contact, get_wc_token):
        more = True
        wc_contact.return_value.json.return_value = {'more': more}
        response = self._call(self._make_request())
        self.assertEqual(more, response['has_more'])

    def test_design_query(self, get_device, wc_contact, get_wc_token):
        loop_id = 'myloop_id'
        self._add_design(loop_id)
        results = [self._make_transfer(loop_id=loop_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(1, len(response['history']))
        transfer = response['history'][0]
        self.assertEqual('myloop_id', transfer['design']['wingcash_id'])

    def test_design_title(self, get_device, wc_contact, get_wc_token):
        self._add_design()
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual('ftitle', transfer['design_title'])     # Old
        self.assertEqual('ftitle', transfer['design']['title'])  # New

    def test_design_logo_image_url(self, get_device, wc_contact, get_wc_token):
        self._add_design()
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_logo_image_url'], 'mylogourl')

    def test_amount_is_returned(self, get_device, wc_contact, get_wc_token):
        amount = 10
        request = self._make_request()
        results = [self._make_transfer(amount=amount)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['amount'], amount)

    def test_timestamp_is_returned(self, get_device, wc_contact, get_wc_token):
        import datetime
        timestamp = datetime.datetime.utcnow()
        request = self._make_request()
        results = [self._make_transfer(timestamp=timestamp)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['timestamp'], timestamp)

    def test_id_is_returned(self, get_device, wc_contact, get_wc_token):
        transfer_id = 'mytransfer_id'
        request = self._make_request()
        results = [self._make_transfer(id=transfer_id)]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['id'], transfer_id)

    def test_multiple_results(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        transfer = self._make_transfer()
        results = [transfer, transfer, transfer]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        self.assertEqual(len(response['history']), len(results))

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

    def test_unrecognized_design(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['design_title'], 'Unrecognized')
        self.assertEqual(transfer['design_logo_image_url'], '')
        self.assertIsNone(transfer['design'])

    def test_unrecognized_customer_role(
            self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        results = [self._make_transfer()]
        wc_contact.return_value.json.return_value = {'results': results}
        response = self._call(request)
        transfer = response['history'][0]
        self.assertEqual(transfer['transfer_type'], 'unrecognized')


@patch('backend.appapi.views.customer_views.get_wc_token')
@patch('backend.appapi.views.customer_views.wc_contact')
@patch('backend.appapi.views.customer_views.get_device')
class TestTransfer(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.customer_views import transfer
        return transfer(*args, **kw)

    def _make_request(self, **kw):
        request_params = {
            'transfer_id': 'defaulttransferid'
        }
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
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

    def test_correct_schema_used(self, get_device, wc_contact, get_wc_token):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.TransferSchema))

    def test_get_device_called(self, get_device, *args):
        request = self._make_request()
        self._call(request)
        get_device.assert_called()

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

    def test_message_is_returned(self, get_device, wc_contact, get_wc_token):
        device = add_device(self.dbsession)[0]
        customer = device.customer
        get_device.return_value = device

        message = 'mymessage'
        transfer = self._make_transfer(
            sender_id=customer.wc_id, message=message)
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response['message'], message)

    def test_sender_counter_party(self, get_device, wc_contact, get_wc_token):
        sender_device = add_device(
            self.dbsession,
            username='senderuser',
            wc_id='11',
            password='senderdev')[0]
        recipient_device = add_device(
            self.dbsession,
            username='recipientuser',
            wc_id='12',
            password='recipientdev')[0]

        get_device.return_value = sender_device
        recipient_device.customer.profile_image_url = (
            'https://profile.example.com/recip.png')

        transfer = self._make_transfer(
            recipient_id=recipient_device.customer.wc_id,
            sender_id=sender_device.customer.wc_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(
            'https://profile.example.com/recip.png',
            response['counter_party_profile_image_url'])

    def test_recipient_counter_party(
            self, get_device, wc_contact, get_wc_token):
        sender_device = add_device(
            self.dbsession,
            username='senderuser',
            wc_id='11',
            password='senderdev')[0]
        recipient_device = add_device(
            self.dbsession,
            username='recipientuser',
            wc_id='12',
            password='recipientdev')[0]

        get_device.return_value = recipient_device
        sender_device.customer.profile_image_url = (
            'https://profile.example.com/sender.png')

        transfer = self._make_transfer(
            recipient_id=recipient_device.customer.wc_id,
            sender_id=sender_device.customer.wc_id)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(
            'https://profile.example.com/sender.png',
            response['counter_party_profile_image_url'])

    def test_permission_denied(self, get_device, wc_contact, get_wc_token):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        transfer = self._make_transfer(
            recipient_id='otherrecipientid', sender_id='othersenderid')
        wc_contact.return_value.json.return_value = transfer
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'permission_denied'})

    def test_business_counter_party_should_have_no_profile_image_url(
            self, get_device, wc_contact, get_wc_token):
        sender_device = add_device(
            self.dbsession,
            username='senderuser',
            wc_id='11',
            password='senderdev')[0]
        recipient_device = add_device(
            self.dbsession,
            username='recipientuser',
            wc_id='12',
            password='recipientdev')[0]

        get_device.return_value = sender_device
        recipient_device.customer.profile_image_url = (
            'https://profile.example.com/recip.png')

        transfer = self._make_transfer(
            recipient_id=recipient_device.customer.wc_id,
            sender_id=sender_device.customer.wc_id,
            recipient_is_individual=False)
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(
            '', response['counter_party_profile_image_url'])

    def test_no_customer_found_for_counter_party(
            self, get_device, wc_contact, get_wc_token):
        sender_device = add_device(
            self.dbsession,
            username='senderuser',
            wc_id='11',
            password='senderdev')[0]

        get_device.return_value = sender_device

        transfer = self._make_transfer(
            sender_id=sender_device.customer.wc_id,
            recipient_id='15')
        wc_contact.return_value.json.return_value = transfer
        request = self._make_request()
        response = self._call(request)
        self.assertEqual('', response['counter_party_profile_image_url'])
