from colander import Schema
from colander import SchemaNode
from colander import String
from backend.api_schemas import amount
from backend.appapi.schemas import app_schemas as schemas


class PurchaseSchema(Schema):
    amount = amount(minimum=0.50)
    design_id = schemas.design_id()
    device_id = schemas.device_id()
    source_id = SchemaNode(String())


class DeleteSourceSchema(Schema):
    device_id = schemas.device_id()
    source_id = SchemaNode(String())
