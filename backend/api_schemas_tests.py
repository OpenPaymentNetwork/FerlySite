from backend.api_schemas import amount
from backend.api_schemas import StrippedString
from colander import Decimal as colanderDecimal
from colander import Invalid
from colander import null
from colander import String
from decimal import Decimal
from unittest import TestCase


class TestAmount(TestCase):

    def _make(self):
        return amount()

    def _call(self, amount=''):
        return self._make().deserialize(amount)

    def test_required(self):
        with self.assertRaisesRegex(Invalid, "'amount': 'Required'"):
            self._call()

    def test_amount_rounds_up(self):
        self.assertEqual(self._call(amount=1.455), Decimal('1.46'))

    def test_amount_rounds_down(self):
        self.assertEqual(self._call(amount=1.454), Decimal('1.45'))

    def test_amount_as_string(self):
        self.assertEqual(self._call(amount='1.02'), Decimal('1.02'))

    def test_amount_as_number(self):
        self.assertEqual(self._call(amount=1.02), Decimal('1.02'))

    def test_is_decimal(self):
        self.assertTrue(isinstance(self._make().typ, colanderDecimal))

    def test_zero(self):
        with self.assertRaisesRegex(Invalid, "'amount': 'Required'"):
            self._call()

    def test_min(self):
        with self.assertRaisesRegex(Invalid, "0.01 is the minimum"):
            self._call(amount=0)


class TestStrippedString(TestCase):

    def _call(self, obj):
        return StrippedString().deserialize(None, obj)

    def test_is_child_of_string(self):
        self.assertTrue(issubclass(StrippedString, String))

    def test_spaces_are_null(self):
        self.assertEqual(self._call('   '), null)

    def test_stripped(self):
        text = 'text'
        padded_text = '  {0}  '.format(text)
        self.assertEqual(self._call(padded_text), text)


# TODO: TestRecipient
