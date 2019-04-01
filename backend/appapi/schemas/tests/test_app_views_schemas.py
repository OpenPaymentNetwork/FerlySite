from backend.appapi.schemas import app_views_schemas
from colander import Invalid
from unittest import TestCase


class TestSearchMarketSchema(TestCase):

    def _call(self, obj={}):
        return app_views_schemas.SearchMarketSchema().deserialize(obj)

    def test_query_required(self):
        with self.assertRaisesRegex(Invalid, "'query': 'Required'"):
            self._call()
