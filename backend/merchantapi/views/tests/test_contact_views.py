from backend.merchantapi.schemas import site_schemas
from backend.merchantapi.views.contact_views import create_contact
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


class TestCreateContact(TestCase):

    def _call(self, *args, **kw):
        return create_contact(*args, **kw)

    def _make_request(self, **kw):
        request_params = {'email': 'defaultemail@example.com'}
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
        request.get_params = params = MagicMock()
        params.return_value = site_schemas.ContactSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, site_schemas.ContactSchema))

    @patch('backend.merchantapi.views.contact_views.Contact')
    def test_contact_created(self, mock_contact):
        email = 'example@example.com'
        request = self._make_request(email=email)
        mcontact = mock_contact.return_value
        self._call(request)
        mock_contact.assert_called_once_with(email=email)
        request.dbsession.add.assert_called_once_with(mcontact)
