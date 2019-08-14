from backend.api_schemas import StrippedString
from backend.appapi.schemas import recovery_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestRecoverySchema(TestCase):

    def _get_schema(self):
        return schemas.RecoverySchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'defaultdeviceid0defaultdeviceid0',
            'login': 'default_login',
        }
        obj.update(**kw)
        return obj

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call()

    def test_login_stripped(self):
        login_type = self._get_schema().get(name='login').typ
        self.assertTrue(isinstance(login_type, StrippedString))


class TestRecoveryCodeSchema(TestCase):

    def _get_schema(self):
        return schemas.RecoveryCodeSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'defaultdeviceid0defaultdeviceid0',
            'code': 'default_code',
            'secret': 'default_secret',
            'factor_id': 'default_factor_id',
            'attempt_path': 'default_attempt_path'
        }
        obj.update(**kw)
        return obj

    def test_code_required(self):
        with self.assertRaisesRegex(Invalid, "'code': 'Required'"):
            self._call()

    def test_secret_required(self):
        with self.assertRaisesRegex(Invalid, "'secret': 'Required'"):
            self._call()

    def test_factor_id_required(self):
        with self.assertRaisesRegex(Invalid, "'factor_id': 'Required'"):
            self._call()

    def test_attempt_path_required(self):
        with self.assertRaisesRegex(Invalid, "'attempt_path': 'Required'"):
            self._call()

    def test_default_recaptcha_response(self):
        response = self._call(self._make())
        self.assertIsNone(response['recaptcha_response'])

    def test_default_os(self):
        response = self._call(self._make())
        self.assertEqual(response['os'], '')

    def test_default_expo_token(self):
        response = self._call(self._make())
        self.assertEqual(response['expo_token'], '')

    def test_code_stripped(self):
        code_type = self._get_schema().get(name='code').typ
        self.assertTrue(isinstance(code_type, StrippedString))


class TestAddUIDSchema(TestCase):

    def _get_schema(self):
        return schemas.AddUIDSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'login': 'default_login',
            'uid_type': 'email'
        }
        obj.update(**kw)
        return obj

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call()

    def test_uid_type_required(self):
        with self.assertRaisesRegex(Invalid, "'uid_type': 'Required'"):
            self._call()

    def test_login_stripped(self):
        login_type = self._get_schema().get(name='login').typ
        self.assertTrue(isinstance(login_type, StrippedString))

    def test_valid_uid_type(self):
        with self.assertRaisesRegex(
                Invalid, "is not one of phone, email"):
            self._call(self._make(uid_type='baduid'))


class TestAddUIDCodeSchema(TestCase):

    def _get_schema(self):
        return schemas.AddUIDCodeSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'defaultdeviceid0defaultdeviceid0',
            'code': 'default_code',
            'secret': 'default_secret',
            'attempt_id': 'default_attempt_id'
        }
        obj.update(**kw)
        return obj

    def test_code_required(self):
        with self.assertRaisesRegex(Invalid, "'code': 'Required'"):
            self._call()

    def test_secret_required(self):
        with self.assertRaisesRegex(Invalid, "'secret': 'Required'"):
            self._call()

    def test_attempt_id_required(self):
        with self.assertRaisesRegex(Invalid, "'attempt_id': 'Required'"):
            self._call()

    def test_default_recaptcha_response(self):
        response = self._call(self._make())
        self.assertIsNone(response['recaptcha_response'])

    def test_default_replace_uid(self):
        response = self._call(self._make())
        self.assertIsNone(response['replace_uid'])

    def test_code_stripped(self):
        code_type = self._get_schema().get(name='code').typ
        self.assertTrue(isinstance(code_type, StrippedString))


class TestAuthUIDCodeSchema(TestCase):

    def _get_schema(self):
        return schemas.AuthUIDCodeSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def test_code_required(self):
        with self.assertRaisesRegex(Invalid, "'code': 'Required'"):
            self._call()

    def test_factor_id_required(self):
        with self.assertRaisesRegex(Invalid, "'factor_id': 'Required'"):
            self._call()

    def test_code_stripped(self):
        code_type = self._get_schema().get(name='code').typ
        self.assertTrue(isinstance(code_type, StrippedString))
