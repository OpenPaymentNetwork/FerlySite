from backend.appapi.schemas import customer_views_schemas as schemas
from colander import Invalid
from decimal import Decimal
from unittest import TestCase


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

    def test_short_username(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must contain at least 4 characters'"):
            self._call(self._make(username='abc'))

    def test_long_username(self):
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must not be longer than 20 characters'"):
            self._call(self._make(username='abcdefghijklmnopqrstu'))

    def test_username_beginning_with_number(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must not start with a number'"):
            self._call(self._make(username='1abc'))

    def test_invalid_symbols_in_username(self):
        invalids = ('!', '@', '#', '$', '%', '^', '&', '*', '+', '-', '~', '?')
        error = "'username': 'Can only contain letters, numbers, and periods'"
        for invalid in invalids:
            with self.subTest():
                username = 'abc{0}'.format(invalid)
                with self.assertRaisesRegex(Invalid, error, msg=username):
                    self._call(self._make(username=username))

    def test_valid_symbols_in_username(self):
        valids = ('a', '1', '.')
        for valid in valids:
            with self.subTest():
                username = 'abc{0}'.format(valid)
                try:
                    response = self._call(self._make(username=username))
                except Invalid:
                    self.fail(username)
                self.assertEqual(response['username'], username)

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

    def _call(self, obj={}):
        return schemas.SendSchema().deserialize(obj)

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

    def test_message_stripped(self):
        message = 'text'
        padded_message = ' {0} '.format(message)
        response = self._call(self._make(message=padded_message))
        self.assertEqual(response['message'], message)

    def test_amount_minimum(self):
        with self.assertRaisesRegex(Invalid, "0.01 is the minimum"):
            self._call(self._make(amount=0))

    def test_amount_rounds_up(self):
        response = self._call(self._make(amount=1.455))
        self.assertEqual(response['amount'], Decimal('1.46'))

    def test_amount_rounds_down(self):
        response = self._call(self._make(amount=1.454))
        self.assertEqual(response['amount'], Decimal('1.45'))

    def test_amount_as_string(self):
        response = self._call(self._make(amount='1.02'))
        self.assertEqual(response['amount'], Decimal('1.02'))

    def test_amount_as_number(self):
        response = self._call(self._make(amount=1.02))
        self.assertEqual(response['amount'], Decimal('1.02'))


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

    def test_short_username(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must contain at least 4 characters'"):
            self._call(self._make(username='abc'))

    def test_long_username(self):
        with self.assertRaisesRegex(
                Invalid,
                "'username': 'Must not be longer than 20 characters'"):
            self._call(self._make(username='abcdefghijklmnopqrstu'))

    def test_username_beginning_with_number(self):
        with self.assertRaisesRegex(
                Invalid, "'username': 'Must not start with a number'"):
            self._call(self._make(username='1abc'))

    def test_invalid_symbols_in_username(self):
        invalids = ('!', '@', '#', '$', '%', '^', '&', '*', '+', '-', '~', '?')
        error = "'username': 'Can only contain letters, numbers, and periods'"
        for invalid in invalids:
            with self.subTest():
                username = 'abc{0}'.format(invalid)
                with self.assertRaisesRegex(Invalid, error, msg=username):
                    self._call(self._make(username=username))

    def test_valid_symbols_in_username(self):
        valids = ('a', '1', '.')
        for valid in valids:
            with self.subTest():
                username = 'abc{0}'.format(valid)
                try:
                    response = self._call(self._make(username=username))
                except Invalid:
                    self.fail(username)
                self.assertEqual(response['username'], username)


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

    def test_image_required(self):
        with self.assertRaisesRegex(Invalid, "'image': 'Required'"):
            self._call()

    # TODO: assert image must be an instance of api_schemas.FieldStorage
