from backend.appapi.schemas import app_schemas
from colander import Invalid
from unittest import TestCase


class TestDeviceSchema(TestCase):

    def _call(self, obj={}):
        return app_schemas.DeviceSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_valid(self):
        obj = {'device_id': 'myid'}
        response = self._call(obj)
        self.assertEqual(response, obj)
