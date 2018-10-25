from backend.views.appviews import create_contact
from colander import Invalid
from pyramid import testing as pyramidtesting
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch


class TestCreateContact(TestCase):

    def _call(self, *args, **kw):
        return create_contact(*args, **kw)

    def test_no_params(self):
        request = pyramidtesting.DummyRequest()
        with self.assertRaises(Invalid) as cm:
            self._call(request)
        e = cm.exception
        expected_response = {'email': 'Required'}
        self.assertEqual(expected_response, e.asdict())

    def test_invalid_email(self):
        invalid_emails = ['123', 'fake@.com', 'abc']
        for invalid_email in invalid_emails:
            request_params = {
                'email': invalid_email
            }
            request = pyramidtesting.DummyRequest(params=request_params)
            with self.assertRaises(Invalid) as cm:
                self._call(request)
            e = cm.exception
            expected_response = {'email': 'Invalid email address'}
            self.assertEqual(expected_response, e.asdict())

    @patch('backend.views.appviews.Contact')
    def test_contact_created(self, mock_contact):
        email = 'example@example.com'
        request_params = {
            'email': email
        }
        request = pyramidtesting.DummyRequest(params=request_params)
        mcontact = mock_contact.return_value
        mdbsession = request.dbsession = MagicMock()
        self._call(request)
        mock_contact.assert_called_once_with(email=email)
        mdbsession.add.assert_called_once_with(mcontact)
