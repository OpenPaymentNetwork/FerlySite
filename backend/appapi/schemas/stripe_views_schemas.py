from colander import SchemaNode
from colander import String
from backend.api_schemas import amount as amount_node
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema


class PurchaseSchema(CustomerDeviceSchema):
    amount = amount_node(minimum=0.50)
    fee = amount_node(name='fee', minimum=0)
    design_id = SchemaNode(String())
    source_id = SchemaNode(String())


class DeleteSourceSchema(CustomerDeviceSchema):
    source_id = SchemaNode(String())
