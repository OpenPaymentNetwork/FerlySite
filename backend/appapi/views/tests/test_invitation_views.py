
from backend.appapi.schemas import invitation_views_schemas as schemas
from backend.database.models import Invitation
from backend.testing import add_device
from backend.testing import DBFixture
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class TestInvite(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import invite
        return invite(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'recipient': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.InviteSchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.invitation_views.send_invite_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_correct_schema_used(self, get_device, send_invite_email):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.InviteSchema))

    @patch('backend.appapi.views.invitation_views.send_invite_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_get_device_called(self, get_device, send_invite_email):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.invitation_views.send_invite_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invitation_added(self, get_device, send_invite_email):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        request = self._make_request()
        self._call(request)
        inv = self.dbsession.query(Invitation).one()
        self.assertEqual(device.customer.id, inv.customer_id)

    @patch('backend.appapi.views.invitation_views.send_invite_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_email_invitation(self, get_device, send_invite_email):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        recipient = 'friendsemail@example.com'
        sendgrid_response = send_invite_email.return_value = '202'
        expected_response = 'sendgrid:{0}'.format(sendgrid_response)
        request = self._make_request(recipient=recipient)
        self._call(request)
        send_invite_email.assert_called_with(
            request,
            recipient,
            'Ferly Invitation',
        )
        inv = self.dbsession.query(Invitation).one()
        self.assertEqual(device.customer.id, inv.customer_id)
        self.assertEqual(recipient, inv.recipient)
        self.assertEqual(expected_response, inv.response)

    @patch('backend.appapi.views.invitation_views.send_sms')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_sms_invitation(self, get_device, send_sms):
        device = add_device(self.dbsession)[0]
        get_device.return_value = device
        recipient = '+12025551234'
        twilio_response = send_sms.return_value = 'queued'
        expected_response = 'twilio:{0}'.format(twilio_response)
        request = self._make_request(recipient=recipient)
        self._call(request)
        send_sms.assert_called_with(
            request,
            recipient,
            'You have been invited to join Ferly. Download the app and get started! https://appurl.io/iO7GkimtW'
        )
        inv = self.dbsession.query(Invitation).one()
        self.assertEqual(device.customer.id, inv.customer_id)
        self.assertEqual(recipient, inv.recipient)
        self.assertEqual(expected_response, inv.response)


class TestExistingInvitations(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import existing_invitations
        return existing_invitations(*args, **kw)

    def _make_request(self, **params):
        request_params = {'deviceToken': 'defaultdeviceToken0defaultdeviceToken0'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.ExistingInvitationsSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _add_invitation(self, customer_id, status='pending'):
        inv = Invitation(
            customer_id=customer_id,
            recipient='friendsemail@example.com',
            response='sendgrid:202',
        )
        self.dbsession.add(inv)
        self.dbsession.flush()
        return inv

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_correct_schema_used(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.ExistingInvitationsSchema))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_get_device_called(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invitations_by_this_customer_only(self, get_device):
        get_device.return_value = device = add_device(self.dbsession)[0]
        other_device = add_device(
            self.dbsession,
            username='other',
            wc_id='12',
            deviceToken='other-user-device')[0]
        inv = self._add_invitation(customer_id=device.customer_id)
        self._add_invitation(customer_id=other_device.customer_id)
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(1, len(response['results']))
        result = response['results'][0]
        self.assertEqual({
            'created': result['created'],
            'id': inv.id,
            'recipient': inv.recipient,
            'status': 'pending',
        }, result)

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_no_status_returns_all(self, get_device):
        get_device.return_value = device = add_device(self.dbsession)[0]
        self._add_invitation(customer_id=device.customer_id)
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(1, len(response['results']))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_status_match(self, get_device):
        get_device.return_value = device = add_device(self.dbsession)[0]
        self._add_invitation(customer_id=device.customer_id)
        request = self._make_request(status='pending')
        response = self._call(request)
        self.assertEqual(1, len(response['results']))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_status_mismatch(self, get_device):
        get_device.return_value = device = add_device(self.dbsession)[0]
        self._add_invitation(customer_id=device.customer_id)
        request = self._make_request(status='accepted')
        response = self._call(request)
        self.assertEqual(0, len(response['results']))


class TestDeleteInvitation(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import delete_invitation
        return delete_invitation(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'invite_id': 'id',
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = schemas.DeleteInvitationSchema().bind(
            request=request).deserialize(request_params)
        return request

    def _add_invitation(self, customer_id, status='pending'):
        inv = Invitation(
            customer_id=customer_id,
            recipient='friendsemail@example.com',
            response='sendgrid:202',
        )
        self.dbsession.add(inv)
        self.dbsession.flush()
        return inv

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_correct_schema_used(self, get_device):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.DeleteInvitationSchema))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_get_device_called(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invite_not_owned(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_non_existing_invite(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        response = self._call(request)
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_status_updated(self, get_device):
        get_device.return_value = device = add_device(self.dbsession)[0]
        invitation = self._add_invitation(customer_id=device.customer.id)
        request = self._make_request(invite_id=invitation.id)
        response = self._call(request)
        self.assertEqual(invitation.status, 'deleted')
        self.assertEqual({}, response)

class TestGetInvalidCodeCount(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import getInvalidCodeCount
        return getInvalidCodeCount(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_get_device_called(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invalid_count_returned(self, get_device):
        get_device.return_value = add_device(self.dbsession,invalidCount='1')[0]
        response = self._call(self._make_request())
        self.assertEqual(response, {'count': '1'})

@patch('backend.appapi.views.invitation_views.wc_contact')
@patch('backend.appapi.views.invitation_views.get_wc_token')
@patch('backend.appapi.views.invitation_views.get_device')
class TestAcceptCode(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import acceptCode
        return acceptCode(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def test_correct_schema_used(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        get_wc_token.return_value = 'test'
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.AcceptCodeSchema))

    def test_get_device_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    def test_get_token_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_once()

    def test_wc_contact_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        wc_contact.assert_called_once()

@patch('backend.appapi.views.invitation_views.get_device')
class TestUpdateInvalidCodeCount(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import updateInvalidCodeCount
        return updateInvalidCodeCount(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def test_correct_schema_used(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.updateInvalidCodeCountSchema))

    def test_get_device_called(self, get_device):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    def test_successful_response(self, get_device):
        deviceCustomer = add_device(self.dbsession,invalidCount='1')
        get_device.return_value = deviceCustomer[0]
        response = self._call(self._make_request())
        self.assertEqual(response, {})

    def test_update_successful(self, get_device):
        from datetime import datetime
        deviceCustomer = add_device(self.dbsession,invalidCount='1')
        get_device.return_value = deviceCustomer[0]
        customer = deviceCustomer[1]
        self._call(self._make_request())
        self.assertEqual(customer.invalid_count, '2')
        self.assertEqual(customer.invalid_date.date(), datetime.now().date())

@patch('backend.appapi.views.invitation_views.wc_contact')
@patch('backend.appapi.views.invitation_views.get_wc_token')
@patch('backend.appapi.views.invitation_views.get_device')
class TestRetract(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import retract
        return retract(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def test_correct_schema_used(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        get_wc_token.return_value = 'test'
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.RetractSchema))

    def test_get_device_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    def test_get_token_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_once()

    def test_wc_contact_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        wc_contact.assert_called_once()

@patch('backend.appapi.views.invitation_views.wc_contact')
@patch('backend.appapi.views.invitation_views.get_wc_token')
@patch('backend.appapi.views.invitation_views.get_device')
class TestGetTransferDetails(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import getTransferDetails
        return getTransferDetails(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def test_correct_schema_used(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        get_wc_token.return_value = 'test'
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.RetractSchema))

    def test_get_device_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    def test_get_token_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_once()

    def test_wc_contact_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        wc_contact.assert_called_once()

@patch('backend.appapi.views.invitation_views.wc_contact')
@patch('backend.appapi.views.invitation_views.get_wc_token')
@patch('backend.appapi.views.invitation_views.get_device')
class TestResend(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.appapi.views.invitation_views import resend
        return resend(*args, **kw)

    def _make_request(self, **kw):
        request = pyramid.testing.DummyRequest(headers={
            'Authorization': 'Bearer defaultdeviceToken0defaultdeviceToken0'})
        request.dbsession = self.dbsession
        request.get_params = kw = MagicMock()
        return request

    def test_correct_schema_used(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        get_wc_token.return_value = 'test'
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.RetractSchema))

    def test_get_device_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_device.assert_called_once()

    def test_get_token_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        get_wc_token.assert_called_once()

    def test_wc_contact_called(self, get_device, get_wc_token, wc_contact):
        get_device.return_value = add_device(self.dbsession)[0]
        request = self._make_request()
        self._call(request)
        wc_contact.assert_called_once()

