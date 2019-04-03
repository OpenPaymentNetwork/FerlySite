from backend.api_schemas import StrippedString
from backend.appapi.schemas import customer_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestUsername(TestCase):

    def _make(self, username=''):
        return schemas.username().deserialize(username)

    def test_is_string(self):
        with self.assertRaisesRegex(Invalid, "is not a string"):
            self._make(104)

    def test_required(self):
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
            self._make()

    def test_too_short(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must contain at least 4 characters'"):
            self._make('abc')

    def test_too_long(self):
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must not be longer than 20 characters'"):
            self._make('abcdefghijklmnopqrstu')

    def test_beginning_with_number(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must not start with a number'"):
            self._make('1abc')

    def test_invalid_symbols(self):
        invalids = ('!', '@', '#', '$', '%', '^', '&', '*', '+', '-', '~', '?')
        error = "'username': 'Can only contain letters, numbers, and periods'"
        for invalid in invalids:
            with self.subTest():
                username = 'abc{0}'.format(invalid)
                with self.assertRaisesRegex(Invalid, error, msg=username):
                    self._make(username)

    def test_valid_symbols_in_username(self):
        valids = ('a', '1', '.')
        for valid in valids:
            with self.subTest():
                username = 'abc{0}'.format(valid)
                try:
                    response = self._make(username=username)
                except Invalid:
                    self.fail(username)
                self.assertEqual(response, username)


class TestName(TestCase):

    def _make(self):
        return schemas.name()

    def _call(self, name=''):
        return self._make().deserialize(name)

    def test_is_string(self):
        with self.assertRaisesRegex(Invalid, "is not a string"):
            self._call(104)

    def test_required(self):
        with self.assertRaisesRegex(Invalid, "'name': 'Required'"):
            self._call()

    def test_one_char(self):
        name = 'a'
        try:
            response = self._call(name=name)
        except Invalid:
            self.fail(name)
        self.assertEqual(response, name)

    def test_too_long(self):
        with self.assertRaisesRegex(
                Invalid, "'name': 'Longer than maximum length 50'"):
            self._call(name='n'*51)

    def test_is_stripped_string(self):
        self.assertTrue(isinstance(self._make().typ, StrippedString))


class TestRegisterSchema(TestCase):

    def _call(self, obj={}):
        return schemas.RegisterSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'first_name': 'default_first_name',
            'last_name': 'default_last_name',
            'username': 'defaultusername'
        }
        obj.update(**kw)
        return obj

    def test_username_required(self):
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
            self._call()

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_first_name_required(self):
        with self.assertRaisesRegex(Invalid, "'first_name': 'Required'"):
            self._call()

    def test_last_name_required(self):
        with self.assertRaisesRegex(Invalid, "'last_name': 'Required'"):
            self._call()

    def test_default_os(self):
        response = self._call(self._make())
        self.assertEqual(response['os'], '')

    def test_default_expo_token(self):
        response = self._call(self._make())
        self.assertEqual(response['expo_token'], '')


class TestIsUserSchema(TestCase):

    def _call(self, obj={}):
        return schemas.IsUserSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_default_expected_env(self):
        response = self._call({'device_id': 'default_device_id'})
        self.assertEqual(response['expected_env'], 'staging')


class TestSendSchema(TestCase):

    def _get_schema(self):
        return schemas.SendSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'design_id': 'default_first_name',
            'recipient_id': 'default_recipient_name',
            'amount': 0.01
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_design_id_required(self):
        with self.assertRaisesRegex(Invalid, "'design_id': 'Required'"):
            self._call()

    def test_recipient_id_required(self):
        with self.assertRaisesRegex(Invalid, "'recipient_id': 'Required'"):
            self._call()

    def test_amount_required(self):
        with self.assertRaisesRegex(Invalid, "'amount': 'Required'"):
            self._call()

    def test_default_message(self):
        response = self._call(self._make())
        self.assertEqual(response['message'], '')

    def test_message_length(self):
        message = 'm' * 501
        with self.assertRaisesRegex(
                Invalid, "'message': 'Longer than maximum length 500'"):
            self._call(self._make(message=message))

    def test_message_is_strippedstring(self):
        message_type = self._get_schema().get(name='message').typ
        self.assertTrue(isinstance(message_type, StrippedString))

    def test_amount_minimum(self):
        with self.assertRaisesRegex(Invalid, "0.01 is the minimum"):
            self._call(self._make(amount=0))


class TestEditProfileSchema(TestCase):

    def _call(self, obj={}):
        return schemas.EditProfileSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'first_name': 'default_first_name',
            'last_name': 'default_last_name',
            'username': 'defaultusername'
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_first_name_required(self):
        with self.assertRaisesRegex(Invalid, "'first_name': 'Required'"):
            self._call()

    def test_last_name_required(self):
        with self.assertRaisesRegex(Invalid, "'last_name': 'Required'"):
            self._call()

    def test_username_required(self):
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
            self._call()


class TestHistorySchema(TestCase):

    def _call(self, obj={}):
        return schemas.HistorySchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {'device_id': 'default_device_id'}
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_default_limit(self):
        response = self._call(self._make())
        self.assertEqual(response['limit'], 100)

    def test_default_offset(self):
        response = self._call(self._make())
        self.assertEqual(response['offset'], 0)

    def test_limit_as_string(self):
        response = self._call(self._make(limit='12'))
        self.assertEqual(response['limit'], 12)

    def test_offset_as_string(self):
        response = self._call(self._make(offset='12'))
        self.assertEqual(response['offset'], 12)

    def test_limit_min(self):
        error = "'limit': '0 is less than minimum value 1'"
        with self.assertRaisesRegex(Invalid, error):
            self._call(self._make(limit=0))

    def test_offset_min(self):
        error = "'offset': '-1 is less than minimum value 0'"
        with self.assertRaisesRegex(Invalid, error):
            self._call(self._make(offset=-1))


class TestTransferSchema(TestCase):

    def _call(self, obj={}):
        return schemas.TransferSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_transfer_id_required(self):
        with self.assertRaisesRegex(Invalid, "'transfer_id': 'Required'"):
            self._call()


class TestSearchUsersSchema(TestCase):

    def _call(self, obj={}):
        return schemas.SearchUsersSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_query_required(self):
        with self.assertRaisesRegex(Invalid, "'query': 'Required'"):
            self._call()


class TestUploadProfileImageSchema(TestCase):

    def _call(self, obj={}):
        return schemas.UploadProfileImageSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    # TODO: assert image is required
    # def test_image_required(self):
    #     with self.assertRaisesRegex(Invalid, "'image': 'Required'"):
    #         self._call()

    # TODO: assert image must be an instance of api_schemas.FieldStorage
