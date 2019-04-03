from backend.appapi.schemas import invitation_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestExistingInvitationSchema(TestCase):

    def _call(self, obj={}):
        return schemas.ExistingInvitationsSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {'device_id': 'default_device_id'}
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

    def _call(self, obj={}):
        return schemas.InviteSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_recipient_required(self):
        with self.assertRaisesRegex(Invalid, "'recipient': 'Required'"):
            self._call()

    # TODO: assert recipient must be an instance of api_schemas.Recipient


class TestDeleteInvitationSchema(TestCase):

    def _call(self, obj={}):
        return schemas.DeleteInvitationSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_invite_id_required(self):
        with self.assertRaisesRegex(Invalid, "'invite_id': 'Required'"):
            self._call()
