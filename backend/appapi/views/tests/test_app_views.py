
from backend.appapi.schemas import app_views_schemas as schemas
from backend.database.models import Design
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
        request = pyramid.testing.DummyRequest(params=request_params)
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

    def test_correct_schema_used(self, wc_contact):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.LocationsSchema))

    def test_invalid_design(self, wc_contact):
        request = self._make_request()
        response = self._call(request)
        self.assertEqual({'error': 'invalid_design'}, response)

    def test_wc_contact_args(self, wc_contact):
        design = self._add_design()
        request = self._make_request(design_id=design.id)
        self._call(request)
        wc_contact.assert_called_with(
            request,
            'GET',
            '/design/{0}/redeemers'.format(design.wc_id),
            anon=True)

    def test_response(self, wc_contact):
        design = self._add_design()
        location = self._make_location()
        wc_contact.return_value.json.return_value = [location]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual([location], response['locations'])

    def test_unwanted_attributes_ignored(self, wc_contact):
        design = self._add_design()
        location = self._make_location()
        revised_location = location.copy()
        revised_location['unwanted_key'] = 'unwanted_value'
        wc_contact.return_value.json.return_value = [revised_location]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual([location], response['locations'])

    def test_multiple_locations(self, wc_contact):
        design = self._add_design()
        locations = wc_contact.return_value.json.return_value = [
            self._make_location(title='title1', address='address1'),
            self._make_location(title='title2', address='address2')
        ]
        response = self._call(self._make_request(design_id=design.id))
        self.assertEqual(locations, response['locations'])
