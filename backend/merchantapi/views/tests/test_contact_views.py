
from backend.merchantapi.schemas import site_schemas
from backend.testing import DBFixture
from unittest import TestCase
from unittest.mock import MagicMock
import pyramid.testing


def setup_module():
    global dbfixture
    dbfixture = DBFixture()


def teardown_module():
    dbfixture.close_fixture()


class TestCreateContact(TestCase):

    def setUp(self):
        self.dbsession, self.close_session = dbfixture.begin_session()

    def tearDown(self):
        self.close_session()

    def _call(self, *args, **kw):
        from backend.merchantapi.views.contact_views import create_contact
        return create_contact(*args, **kw)

    def _make_request(self, **kw):
        request_params = {'email': 'defaultemail@example.com'}
        request_params.update(**kw)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = self.dbsession
        request.get_params = params = MagicMock()
        params.return_value = site_schemas.ContactSchema().bind(
            request=request).deserialize(request_params)
        return request

    def test_correct_schema_used(self):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, site_schemas.ContactSchema))

    def test_contact_created(self):
        from backend.database.models import Contact
        email = 'example@example.com'
        request = self._make_request(email=email)
        self._call(request)
        contact = self.dbsession.query(Contact).one()
        self.assertEqual(email, contact.email)
