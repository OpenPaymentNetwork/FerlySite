from backend.appapi.schemas import app_schemas
from colander import Invalid
from unittest import TestCase


class TestCustomerDeviceSchema(TestCase):

    def _call(self, obj={}):
        return app_schemas.CustomerDeviceSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_valid(self):
        obj = {'device_id': 'myid' * 8}
        response = self._call(obj)
        self.assertEqual(response, obj)

    def test_too_short(self):
        obj = {'device_id': 'myid'}
        with self.assertRaisesRegex(Invalid, "Shorter than minimum length"):
            self._call(obj)

    def test_too_long(self):
        obj = {'device_id': 'myid' * 51}
        with self.assertRaisesRegex(Invalid, "Longer than maximum length"):
            self._call(obj)
