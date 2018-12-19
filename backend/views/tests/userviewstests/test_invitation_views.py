from backend.models.models import Invitation
from backend.views.userviews.invitationviews import delete_invitation
from backend.views.userviews.invitationviews import existing_invitations
from backend.views.userviews.invitationviews import invite
from colander import Invalid
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
        return request

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_recipient_required(self):
        with self.assertRaisesRegex(Invalid, "'recipient': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    @patch('backend.views.userviews.invitationviews.get_device')
    @patch('backend.views.userviews.invitationviews.Invitation')
    def test_invitation_params(self, invitation, get_device):
        recipient = 'friendsemail@example.com'
        request = self._make_request(recipient=recipient)
        user = get_device.return_value.user
        self._call(request)
        invitation.assert_called_with(user_id=user.id, recipient=recipient)

    @patch('backend.views.userviews.invitationviews.get_device')
    @patch('backend.views.userviews.invitationviews.Invitation')
    def test_invitation_added(self, invitation, get_device):
        request = self._make_request()
        mock_invitation = invitation.return_value
        self._call(request)
        request.dbsession.add.assert_called_with(mock_invitation)


class TestExistingInvitations(TestCase):

    def _call(self, *args, **kw):
        return existing_invitations(*args, **kw)

    def _make_request(self, **params):
        request_params = {'device_id': 'defaultdeviceid'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        return request

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_invalid_status(self):
        status = 'expired'
        request = self._make_request(status=status)
        error = '"{0}" is not one of pending, deleted, accepted'.format(status)
        with self.assertRaisesRegex(Invalid, "'status': '{0}'".format(error)):
            self._call(request)

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_invitations_by_this_user_only(self, get_device):
        request = self._make_request()
        user = get_device.return_value.user
        user_filter = request.dbsession.query.return_value.filter
        self._call(request)
        expression = Invitation.user_id == user.id
        self.assertTrue(expression.compare(user_filter.call_args[0][0]))

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_no_status_returns_all(self, get_device):
        request = self._make_request()
        all_call = request.dbsession.query.return_value.filter.return_value.all
        self._call(request)
        self.assertTrue(all_call.called)

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_status_applies_filter(self, get_device):
        status = 'pending'
        request = self._make_request(status=status)
        status_filter = request.dbsession.query().filter().filter
        self._call(request)
        expression = Invitation.status == status
        self.assertTrue(expression.compare(status_filter.call_args[0][0]))

    @patch('backend.views.userviews.invitationviews.serialize_invitation')
    @patch('backend.views.userviews.invitationviews.get_device')
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
        return request

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    def test_invite_id_required(self):
        with self.assertRaisesRegex(Invalid, "'invite_id': 'Required'"):
            self._call(pyramid.testing.DummyRequest(params={}))

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_invite_not_owned(self, get_device):
        response = self._call(self._make_request())
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_non_existing_invite(self, get_device):
        request = self._make_request()
        request.dbsession.query().get().return_value = None
        response = self._call(request)
        self.assertEqual(response, {'error': 'cannot_be_deleted'})

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_status_updated(self, get_device):
        request = self._make_request()
        user_id = 'myuser_id'
        invitation = request.dbsession.query().get.return_value
        invitation.user_id = user_id
        get_device.return_value.user.id = user_id
        self._call(request)
        self.assertEqual(invitation.status, 'deleted')

    @patch('backend.views.userviews.invitationviews.get_device')
    def test_response(self, get_device):
        request = self._make_request()
        user_id = 'myuser_id'
        invitation = request.dbsession.query().get.return_value
        invitation.user_id = user_id
        get_device.return_value.user.id = user_id
        response = self._call(request)
        self.assertEqual(response, {})
