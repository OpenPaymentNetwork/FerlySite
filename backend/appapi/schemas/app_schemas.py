from colander import Schema
from colander import SchemaNode
from colander import String


class CustomerDeviceSchema(Schema):
    device_id = SchemaNode(String())
