from backend.appapi.schemas import recovery_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestRecoverySchema(TestCase):

    def _call(self, obj={}):
        return schemas.RecoverySchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {'device_id': 'default_device_id', 'login': 'default_login'}
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call()

    def test_login_stripped(self):
        login = 'text'
        padded_login = ' {0} '.format(login)
        response = self._call(self._make(login=padded_login))
        self.assertEqual(response['login'], login)


class TestRecoveryCodeSchema(TestCase):

    def _call(self, obj={}):
        return schemas.RecoveryCodeSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'code': 'default_code',
            'secret': 'default_secret',
            'factor_id': 'default_factor_id',
            'attempt_path': 'default_attempt_path'
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

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
        code = 'text'
        padded_code = ' {0} '.format(code)
        response = self._call(self._make(code=padded_code))
        self.assertEqual(response['code'], code)


class TestAddUIDSchema(TestCase):

    def _call(self, obj={}):
        return schemas.AddUIDSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'login': 'default_login',
            'uid_type': 'email'
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_login_required(self):
        with self.assertRaisesRegex(Invalid, "'login': 'Required'"):
            self._call()

    def test_uid_type_required(self):
        with self.assertRaisesRegex(Invalid, "'uid_type': 'Required'"):
            self._call()

    def test_login_stripped(self):
        login = 'text'
        padded_login = ' {0} '.format(login)
        response = self._call(self._make(login=padded_login))
        self.assertEqual(response['login'], login)

    def test_valid_uid_type(self):
        with self.assertRaisesRegex(
                Invalid, "is not one of phone, email"):
            self._call(self._make(uid_type='baduid'))


class TestAddUIDCodeSchema(TestCase):

    def _call(self, obj={}):
        return schemas.AddUIDCodeSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'code': 'default_code',
            'secret': 'default_secret',
            'attempt_id': 'default_attempt_id'
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

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
        code = 'text'
        padded_code = ' {0} '.format(code)
        response = self._call(self._make(code=padded_code))
        self.assertEqual(response['code'], code)
