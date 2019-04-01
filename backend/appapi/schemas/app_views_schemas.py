from colander import Schema
from colander import SchemaNode
from colander import String


class SearchMarketSchema(Schema):
    query = SchemaNode(String())
