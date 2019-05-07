from backend.appapi.schemas import app_views_schemas as schemas
from backend.appapi.views.app_views import locations
from backend.database.models import Design
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch
import pyramid.testing


@patch('backend.appapi.views.app_views.wc_contact')
class TestLocationsCard(TestCase):

    def _call(self, *args, **kw):
        return locations(*args, **kw)

    def _make_request(self, **params):
        request_params = {'design_id': 'default_design_id'}
        request_params.update(**params)
        request = pyramid.testing.DummyRequest(params=request_params)
        request.dbsession = MagicMock()
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

    def test_correct_schema_used(self, wc_contact):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.LocationsSchema))

    def test_design_query(self, wc_contact):
        design_id = 'my_device_id'
        request = self._make_request(design_id=design_id)
        query = request.dbsession.query
        self._call(request)
        query.assert_called_once_with(Design)
        query.return_value.get.assert_called_once_with(design_id)

    def test_invalid_design(self, wc_contact):
        request = self._make_request()
        request.dbsession.query.return_value.get.return_value = None
        response = self._call(request)
        self.assertEqual({'error': 'invalid_design'}, response)

    def test_wc_contact_args(self, wc_contact):
        request = self._make_request(design_id='my_design_id')
        design = request.dbsession.query.return_value.get.return_value
        self._call(request)
        wc_contact.assert_called_with(
            request, 'GET', '/design/{0}/redeemers'.format(design.wc_id))

    def test_response(self, wc_contact):
        location = self._make_location()
        wc_contact.return_value.json.return_value = [location]
        response = self._call(self._make_request())
        self.assertEqual([location], response['locations'])

    def test_unwanted_attributes_ignored(self, wc_contact):
        location = self._make_location()
        bad_location = location.copy()
        bad_location['bad_key'] = 'bad_value'
        wc_contact.return_value.json.return_value = [bad_location]
        response = self._call(self._make_request())
        self.assertEqual([location], response['locations'])

    def test_multiple_locations(self, wc_contact):
        locations = wc_contact.return_value.json.return_value = [
            self._make_location(title='title1', address='address1'),
            self._make_location(title='title2', address='address2')
        ]
        response = self._call(self._make_request())
        self.assertEqual(locations, response['locations'])
