from backend.appapi.schemas import invitation_views_schemas as schemas
from backend.database.models import Invitation
from backend.appapi.views.invitation_views import delete_invitation
from backend.appapi.views.invitation_views import existing_invitations
from backend.appapi.views.invitation_views import invite
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestInvite(TestCase):

    def _call(self, *args, **kw):
        return invite(*args, **kw)

    def _make_request(self, **params):
        request_params = {
            'device_id': 'defaultdeviceid',
            'recipient': 'email@example.com'
        }
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.InviteSchema().bind(
            request=request).deserialize(request_params)
        return request

    @patch('backend.appapi.views.invitation_views.send_email')
    def test_correct_schema_used(self, send_email):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.InviteSchema))

    @patch('backend.appapi.views.invitation_views.send_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    @patch('backend.appapi.views.invitation_views.Invitation')
    def test_invitation_added(self, invitation, get_device, send_email):
        request = self._make_request()
        mock_invitation = invitation.return_value
        self._call(request)
        request.dbsession.add.assert_called_with(mock_invitation)

    @patch('backend.appapi.views.invitation_views.send_email')
    @patch('backend.appapi.views.invitation_views.get_device')
    @patch('backend.appapi.views.invitation_views.Invitation')
    def test_email_invitation(self, invitation, get_device, send_email):
        recipient = 'friendsemail@example.com'
        sendgrid_response = send_email.return_value = '202'
        expected_response = 'sendgrid:{0}'.format(sendgrid_response)
        request = self._make_request(recipient=recipient)
        user = get_device.return_value.user
        self._call(request)
        send_email.assert_called_with(
            request,
            recipient,
            'Ferly Invitation',
            'You have been invited to join Ferly.'
        )
        invitation.assert_called_with(
            user_id=user.id, recipient=recipient, response=expected_response)

    @patch('backend.appapi.views.invitation_views.send_sms')
    @patch('backend.appapi.views.invitation_views.get_device')
    @patch('backend.appapi.views.invitation_views.Invitation')
    def test_sms_invitation(self, invitation, get_device, send_sms):
        recipient = '+12025551234'
        twilio_response = send_sms.return_value = 'queued'
        expected_response = 'twilio:{0}'.format(twilio_response)
        request = self._make_request(recipient=recipient)
        user = get_device.return_value.user
        self._call(request)
        send_sms.assert_called_with(
            request,
            recipient,
            'You have been invited to join Ferly.'
        )
        invitation.assert_called_with(
            user_id=user.id, recipient=recipient, response=expected_response)


class TestExistingInvitations(TestCase):

    def _call(self, *args, **kw):
        return existing_invitations(*args, **kw)

    def _make_request(self, **params):
        request_params = {'device_id': 'defaultdeviceid'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.ExistingInvitationsSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.ExistingInvitationsSchema))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invitations_by_this_user_only(self, get_device):
        request = self._make_request()
        user = get_device.return_value.user
        user_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Invitation.user_id == user.id
        self.assertTrue(expression.compare(user_filter.call_args[0][0]))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_no_status_returns_all(self, get_device):
        request = self._make_request()
        all_call = request.dbsession.query.return_value.filter.return_value.all
        self._call(request)
        self.assertTrue(all_call.called)

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_status_applies_filter(self, get_device):
        status = 'pending'
        request = self._make_request(status=status)
        status_filter = request.dbsession.query().filter().filter
        self._call(request)
        expression = Invitation.status == status
        self.assertTrue(expression.compare(status_filter.call_args[0][0]))

    @patch('backend.appapi.views.invitation_views.serialize_invitation')
    @patch('backend.appapi.views.invitation_views.get_device')
    def test_results(self, get_device, serialize_invitation):
        request = self._make_request()
        r = request.dbsession.query().filter().all.return_value = [MagicMock()]
        response = self._call(request)
        self.assertEqual(response, {
            'results': [serialize_invitation(request, x) for x in r]})


class TestDeleteInvitation(TestCase):

    def _call(self, *args, **kw):
        return delete_invitation(*args, **kw)

    def _make_request(self, **params):
        request_params = {'device_id': 'defaultdeviceid', 'invite_id': 'id'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = schemas.DeleteInvitationSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(
            isinstance(schema_used, schemas.DeleteInvitationSchema))

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_invite_not_owned(self, get_device):
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_non_existing_invite(self, get_device):
        request = self._make_request()
        request.dbsession.query().get().return_value = None
        response = self._call(request)
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_status_updated(self, get_device):
        request = self._make_request()
        user_id = 'myuser_id'
        invitation = request.dbsession.query().get.return_value
        invitation.user_id = user_id
        get_device.return_value.user.id = user_id
        self._call(request)
        self.assertEqual(invitation.status, 'deleted')

    @patch('backend.appapi.views.invitation_views.get_device')
    def test_response(self, get_device):
        request = self._make_request()
        user_id = 'myuser_id'
        invitation = request.dbsession.query().get.return_value
        invitation.user_id = user_id
        get_device.return_value.user.id = user_id
        response = self._call(request)
        self.assertEqual(response, {})
