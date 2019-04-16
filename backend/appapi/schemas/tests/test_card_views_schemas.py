from backend.api_schemas import StrippedString
from backend.appapi.schemas import card_views_schemas as schemas
from colander import Invalid
from unittest import TestCase


class TestSendSchema(TestCase):

    def _get_schema(self):
        return schemas.AddCardSchema()

    def _call(self, obj={}):
        return self._get_schema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'pan': '1234123412341234',
            'pin': '1234'
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_pan_required(self):
        with self.assertRaisesRegex(Invalid, "'pan': 'Required'"):
            self._call()

    def test_pin_required(self):
        with self.assertRaisesRegex(Invalid, "'pin': 'Required'"):
            self._call()

    def test_short_pin(self):
        with self.assertRaisesRegex(
                Invalid, "'pin': 'Must be exactly 4 digits'"):
            self._call(self._make(pin='123'))

    def test_long_pin(self):
        with self.assertRaisesRegex(
                Invalid, "'pin': 'Must be exactly 4 digits'"):
            self._call(self._make(pin='12345'))

    def test_short_pan(self):
        with self.assertRaisesRegex(
                Invalid, "'pan': 'Must be exactly 16 digits'"):
            self._call(self._make(pan='123412341234123'))

    def test_long_pan(self):
        with self.assertRaisesRegex(
                Invalid, "'pan': 'Must be exactly 16 digits'"):
            self._call(self._make(pan='12341234123412345'))

    def test_alpha_in_pan(self):
        with self.assertRaisesRegex(
                Invalid, "'pan': 'Must contain only numbers'"):
            self._call(self._make(pan='abcdabcdabcdabcd'))

    def test_alpha_in_pin(self):
        with self.assertRaisesRegex(
                Invalid, "'pin': 'Must contain only numbers'"):
            self._call(self._make(pin='abcd'))

    def test_pan_is_strippedstring(self):
        pan_type = self._get_schema().get(name='pan').typ
        self.assertTrue(isinstance(pan_type, StrippedString))

    def test_pin_is_strippedstring(self):
        pin_type = self._get_schema().get(name='pin').typ
        self.assertTrue(isinstance(pin_type, StrippedString))

    def test_invalid_pan_checksum(self):
        invalids = ('4532015112930366', '6012514433546201', '6771549495586602')
        error = 'Invalid card number'
        for invalid in invalids:
            with self.subTest():
                with self.assertRaisesRegex(Invalid, error, msg=invalid):
                    self._call(self._make(pan=invalid))

    def test_valid_pan_checksum(self):
        valids = ('4532015112830366', '6011514433546201', '6771549495586802',
                  '6744322913744542', '4747474747474747', '0715186095371731')
        for valid in valids:
            with self.subTest():
                try:
                    response = self._call(self._make(pan=valid))
                except Invalid:
                    self.fail(valid)
                self.assertEqual(response['pan'], valid)
