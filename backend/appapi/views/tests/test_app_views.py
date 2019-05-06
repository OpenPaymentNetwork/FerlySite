from backend.appapi.schemas import app_views_schemas as schemas
from backend.appapi.views.app_views import locations
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

    def test_correct_schema_used(self, wc_contact):
        request = self._make_request()
        self._call(request)
        schema_used = request.get_params.call_args[0][0]
        self.assertTrue(isinstance(schema_used, schemas.LocationsSchema))

    def test_wc_contact_args(self, wc_contact):
        request = self._make_request(design_id='my_design_id')
        self._call(request)
        wc_contact.assert_called_with(
            request, 'GET', '/design/my_design_id/redeemers')

    def test_response(self, wc_contact):
        location = {'title': 'title1', 'address': 'address1'}
        wc_contact.return_value.json.return_value = [location]
        response = self._call(self._make_request())
        self.assertEqual([location], response['locations'])

    def test_unwanted_attributes_ignored(self, wc_contact):
        location = {'title': 'title1', 'address': 'address1'}
        bad_location = location.copy()
        bad_location['bad_key'] = 'bad_value'
        wc_contact.return_value.json.return_value = [bad_location]
        response = self._call(self._make_request())
        self.assertEqual([location], response['locations'])

    def test_multiple_locations(self, wc_contact):
        locations = wc_contact.return_value.json.return_value = [
            {'title': '', 'address': 'address1'},
            {'title': 'title2', 'address': ''}
        ]
        response = self._call(self._make_request())
        self.assertEqual(locations, response['locations'])
