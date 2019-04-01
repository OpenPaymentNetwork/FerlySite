from backend.appapi.schemas import stripe_views_schemas as schemas
from colander import Invalid
from decimal import Decimal
from unittest import TestCase


class TestDeleteSourceSchema(TestCase):

    def _call(self, obj={}):
        return schemas.DeleteSourceSchema().deserialize(obj)

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_source_id_required(self):
        with self.assertRaisesRegex(Invalid, "'source_id': 'Required'"):
            self._call()


class TestPurchaseSchema(TestCase):

    def _call(self, obj={}):
        return schemas.PurchaseSchema().deserialize(obj)

    def _make(self, *args, **kw):
        obj = {
            'device_id': 'default_device_id',
            'design_id': 'default_design_id',
            'source_id': 'default_source_id',
            'amount': 0.01
        }
        obj.update(**kw)
        return obj

    def test_device_id_required(self):
        with self.assertRaisesRegex(Invalid, "'device_id': 'Required'"):
            self._call()

    def test_source_id_required(self):
        with self.assertRaisesRegex(Invalid, "'source_id': 'Required'"):
            self._call()

    def test_design_id_required(self):
        with self.assertRaisesRegex(Invalid, "'source_id': 'Required'"):
            self._call()

    def test_amount_minimum(self):
        with self.assertRaisesRegex(Invalid, "0.50 is the minimum"):
            self._call(self._make(amount=0.4))

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
