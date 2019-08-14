from backend.appapi.schemas import stripe_views_schemas as schemas
from colander import Invalid
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
            'device_id': 'defaultdeviceid0defaultdeviceid0',
            'design_id': 'default_design_id',
            'source_id': 'default_source_id',
            'amount': 0.51,
            'fee': 0.01
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

    def test_fee_required(self):
        with self.assertRaisesRegex(Invalid, "'fee': 'Required'"):
            self._call()

    def test_amount_minimum(self):
        with self.assertRaisesRegex(Invalid, "0.50 is the minimum"):
            self._call(self._make(amount=0.4))
