
from colander import Length
from colander import Schema
from colander import SchemaNode
from colander import String


class CustomerDeviceSchema(Schema):
    # To maintain a high probability of device_id randomness and
    # unguessability, require at least 32 characters.
    device_id = SchemaNode(String(), validator=Length(min=32, max=200))
