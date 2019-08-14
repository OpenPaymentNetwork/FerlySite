from backend.api_schemas import Recipient
from backend.appapi.schemas import invitation_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestExistingInvitationSchema(TestCase):

    def _call(self, obj={}):
        return schemas.ExistingInvitationsSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {'device_id': 'defaultdeviceid0defaultdeviceid0'}
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_default_status(self):
        response = self._call(self._make())
        self.assertIsNone(response['status'])

    def test_valid_status(self):
        with self.assertRaisesRegex(
                Invalid, "is not one of pending, deleted, accepted"):
            self._call(self._make(status='badstatus'))


class TestInviteSchema(TestCase):

    def _get_schema(self):
        return schemas.InviteSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_recipient_required(self):
        with self.assertRaisesRegex(Invalid, "'recipient': 'Required'"):
            self._call()

    def test_is_recipient(self):
        recipient_type = self._get_schema().get(name='recipient').typ
        self.assertTrue(isinstance(recipient_type, Recipient))


class TestDeleteInvitationSchema(TestCase):

    def _call(self, obj={}):
        return schemas.DeleteInvitationSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_invite_id_required(self):
        with self.assertRaisesRegex(Invalid, "'invite_id': 'Required'"):
            self._call()
