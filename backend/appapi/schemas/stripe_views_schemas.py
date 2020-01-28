from colander import Length
from colander import SchemaNode
from colander import String
from colander import Schema
from backend.api_schemas import amount as amount_node


class PurchaseSchema(Schema):
    amount = amount_node(minimum=0.50)
    fee = amount_node(name='fee', minimum=0)
    design_id = SchemaNode(String(), validator=Length(max=100))
    source_id = SchemaNode(String(), validator=Length(max=100))


class DeleteSourceSchema(Schema):
    source_id = SchemaNode(String(), validator=Length(max=100))
