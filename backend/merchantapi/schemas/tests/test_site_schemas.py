from backend.api_schemas import StrippedString
from backend.merchantapi.schemas import site_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestAuthUIDCodeSchema(TestCase):

    def _get_schema(self):
        return schemas.ContactSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def test_email_required(self):
        with self.assertRaisesRegex(Invalid, "'email': 'Required'"):
            self._call()

    def test_email_stripped(self):
        email = self._get_schema().get(name='email').typ
        self.assertTrue(isinstance(email, StrippedString))

    def test_email_validation(self):
        with self.assertRaisesRegex(
                Invalid, "'email': 'Invalid email address'"):
            self._call({'email': 'bademail'})
