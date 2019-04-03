from colander import SchemaNode
from colander import String
from backend.api_schemas import amount
from backend.appapi.schemas.app_schemas import CustomerDeviceSchema


class PurchaseSchema(CustomerDeviceSchema):
    amount = amount(minimum=0.50)
    design_id = SchemaNode(String())
    source_id = SchemaNode(String())


class DeleteSourceSchema(CustomerDeviceSchema):
    source_id = SchemaNode(String())
