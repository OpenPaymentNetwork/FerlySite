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


class TestAddressSchema(TestCase):

    def _get_schema(self):
        return schemas.AddressSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'name': 'default_name',
            'line1': 'default_line1',
            'city': 'default_city',
            'state': 'UT',
            'zip_code': '84062'
        }
        obj.update(**kw)
        return obj

    def test_name_required(self):
        with self.assertRaisesRegex(Invalid, "'name': 'Required'"):
            self._call()

    def test_line1_required(self):
        with self.assertRaisesRegex(Invalid, "'line1': 'Required'"):
            self._call()

    def test_city_required(self):
        with self.assertRaisesRegex(Invalid, "'city': 'Required'"):
            self._call()

    def test_state_required(self):
        with self.assertRaisesRegex(Invalid, "'state': 'Required'"):
            self._call()

    def test_zip_code_required(self):
        with self.assertRaisesRegex(Invalid, "'zip_code': 'Required'"):
            self._call()

    def test_name_max_length(self):
        name = 'n' * 51
        with self.assertRaisesRegex(
                Invalid, "'name': 'Longer than maximum length 50'"):
            self._call(self._make(name=name))

    def test_line1_max_length(self):
        line = 'l' * 51
        with self.assertRaisesRegex(
                Invalid, "'line1': 'Longer than maximum length 50'"):
            self._call(self._make(line1=line))

    def test_line2_max_length(self):
        line = 'l' * 51
        with self.assertRaisesRegex(
                Invalid, "'line2': 'Longer than maximum length 50'"):
            self._call(self._make(line2=line))

    def test_city_max_length(self):
        with self.assertRaisesRegex(
                Invalid, "'city': 'Longer than maximum length 100'"):
            self._call(self._make(city='City ' * 21))

    def test_name_is_strippedstring(self):
        typ = self._get_schema().get(name='name').typ
        self.assertTrue(isinstance(typ, StrippedString))

    def test_line1_is_strippedstring(self):
        typ = self._get_schema().get(name='line1').typ
        self.assertTrue(isinstance(typ, StrippedString))

    def test_line2_is_strippedstring(self):
        typ = self._get_schema().get(name='line2').typ
        self.assertTrue(isinstance(typ, StrippedString))

    def test_state_invalids(self):
        invalids = ('U1', 'Ute', 'U')
        error = "'state': 'Must be two letters'"
        for invalid in invalids:
            with self.subTest():
                with self.assertRaisesRegex(Invalid, error, msg=invalid):
                    self._call(self._make(state=invalid))

    def test_zip_code_invalids(self):
        invalids = ('8460a', '846023', '8460')
        error = "'zip_code': 'Must be five digits'"
        for invalid in invalids:
            with self.subTest():
                with self.assertRaisesRegex(Invalid, error, msg=invalid):
                    self._call(self._make(zip_code=invalid))


class TestRegisterSchema(TestCase):

    def _call(self, obj={}):
        return schemas.RegisterSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'first_name': 'default_first_name',
            'last_name': 'default_last_name',
            'username': 'blahblah',
            'profile_id': 'myprofileid',
        }
        obj.update(**kw)
        return obj

    def test_username_required(self):
        with self.assertRaisesRegex(Invalid, "'username': 'Required'"):
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


class TestIsCustomerSchema(TestCase):

    def _call(self, obj={}):
        return schemas.IsCustomerSchema().deserialize(obj)

    def test_expected_env_required(self):
        with self.assertRaisesRegex(Invalid, "'expected_env': 'Required'"):
            self._call()


class TestSendSchema(TestCase):

    def _get_schema(self):
        return schemas.SendSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'design_id': 'default_first_name',
            'recipient_id': 'default_recipient_name',
            'amount': 0.01
        }
        obj.update(**kw)
        return obj

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
            'first_name': 'default_first_name',
            'last_name': 'default_last_name',
            'username': 'defaultusername'
        }
        obj.update(**kw)
        return obj

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
        obj = {'deviceToken': 'defaultdeviceToken0defaultdeviceToken0'}
        obj.update(**kw)
        return obj

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

    def test_transfer_id_required(self):
        with self.assertRaisesRegex(Invalid, "'transfer_id': 'Required'"):
            self._call()


class TestSearchCustomersSchema(TestCase):

    def _call(self, obj={}):
        return schemas.SearchCustomersSchema().deserialize(obj)

    def test_query_required(self):
        with self.assertRaisesRegex(Invalid, "'query': 'Required'"):
            self._call()


class TestUploadProfileImageSchema(TestCase):

    def _call(self, obj={}):
        return schemas.UploadProfileImageSchema().deserialize(obj)

    # TODO: assert image is required
    # def test_image_required(self):
    #     with self.assertRaisesRegex(Invalid, "'image': 'Required'"):
    #         self._call()

    # TODO: assert image must be an instance of api_schemas.FieldStorage
