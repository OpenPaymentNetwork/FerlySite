from colander.compat import text_
from colander import Regex
from colander import Schema
from colander import SchemaNode
from backend.api_schemas import StrippedString
import translationstring
_ = translationstring.TranslationStringFactory('colander')

EMAIL_RE = (
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9]+[.]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


class Email(Regex):
    """ Email address validator. If ``msg`` is supplied, it will be
        the error message to be used when raising :exc:`colander.Invalid`;
        otherwise, defaults to 'Invalid email address'.
    """

    def __init__(self, msg=None):
        email_regex = text_(EMAIL_RE)
        if msg is None:
            msg = _("Invalid email address")
        super(Email, self).__init__(email_regex, msg=msg)
class ContactSchema(Schema):
    email = SchemaNode(StrippedString(), validator=Email())
