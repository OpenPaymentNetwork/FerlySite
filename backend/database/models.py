
from .meta import Base
from .meta import string_sequencer
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

now_utc = func.timezone('UTC', func.current_timestamp())


class SequenceKey(Base):
    """Contains the skip32 keys for generating sequences."""
    __tablename__ = 'sequence_key'
    seq_name = Column(
        String, primary_key=True, nullable=False)
    key_index = Column(
        Integer, primary_key=True, nullable=False, autoincrement=False)
    skip32_key = Column(BYTEA(10), nullable=False)


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('customer_seq'))
    wc_id = Column(
        String, nullable=False, index=True, unique=True)
    # XXX the title column attribute is not usable because it's shadowed by
    # the title property below. Should we delete the title column? Find out
    # whether the database actually uses it.
    title = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    profile_image_url = Column(String)
    # recents is a list of recent Ferly customers the customer has sent to.
    recents = Column(ARRAY(String), nullable=False, default=[])
    tsvector = Column(TSVECTOR)
    stripe_id = Column(String)

    @property
    def title(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def update_tsvector(self):
        text_parts = [self.first_name, self.last_name, self.username]
        tsvector = func.to_tsvector(text_parts[0])
        for text_part in text_parts[1:]:
            tsvector = tsvector.concat(func.to_tsvector(text_part))
        self.tsvector = tsvector


class Device(Base):
    __tablename__ = 'device'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('device_seq'))
    # token_sha256 is the sha-256 hex digest of the token that authenticates
    # the device. The token is called "deviceToken" in API calls. Note that for
    # security, this database stores only the digest (aka hash) of the token,
    # not the token itself. Otherwise, an attacker who gets a copy of the
    # database would be able to authenticate as any Ferly user.
    token_sha256 = Column(String, nullable=False, index=True, unique=True)
    customer_id = Column(
        String, ForeignKey('customer.id'), nullable=False)
    expo_token = Column(String)
    last_used = Column(DateTime, nullable=False, server_default=now_utc)
    os = Column(String)

    customer = relationship(Customer)


class Design(Base):
    __tablename__ = 'design'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('design_seq'))
    distribution_id = Column(String)
    wc_id = Column(String, nullable=False)
    title = Column(String)
    listable = Column(Boolean, nullable=False, server_default='True')
    logo_image_url = Column(String)
    wallet_image_url = Column(String)
    fee = Column(Numeric, nullable=False)
    field_color = Column(String, nullable=True)
    field_dark = Column(Boolean, nullable=True)
    tsvector = Column(TSVECTOR)

    def update_tsvector(self):
        self.tsvector = func.to_tsvector(self.title)


class Contact(Base):
    __tablename__ = 'contact'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('contact_seq'))
    email = Column(String, nullable=False)


class Invitation(Base):
    __tablename__ = 'invitation'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('invitation_seq'))
    customer_id = Column(
        String, ForeignKey('customer.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    recipient = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default='pending')
    response = Column(String)

    customer = relationship(Customer)


class CardRequest(Base):
    __tablename__ = 'card_request'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('card_request_seq'))
    customer_id = Column(
        String, ForeignKey('customer.id'), nullable=False, index=True)
    name = Column(Unicode, nullable=False)
    # original_* contains the address input from the customer.
    original_line1 = Column(Unicode, nullable=False)
    original_line2 = Column(Unicode, nullable=True)
    original_city = Column(Unicode, nullable=False)
    original_state = Column(Unicode, nullable=False)
    original_zip_code = Column(Unicode, nullable=False)
    # line1, line2, city, state, and zip_code are normalized by the USPS
    # address info service.
    line1 = Column(Unicode, nullable=False)
    line2 = Column(Unicode, nullable=True)
    city = Column(Unicode, nullable=False)
    state = Column(Unicode, nullable=False)
    zip_code = Column(Unicode, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    downloaded = Column(DateTime, nullable=True)
    verified = Column(Unicode, nullable=False, server_default='')


class StaffToken(Base):
    """An access token for a staff member.

    Staff members authenticate through Amazon Cognito.
    """
    __tablename__ = 'staff_token'
    id = Column(BigInteger, nullable=False, primary_key=True)
    # The secret is a random Fernet encryption key and stored in a cookie.
    # secret_sha256 is the SHA-256 hex digest of the secret.
    secret_sha256 = Column(String, nullable=False)
    # The tokens_fernet column contains Fernet encrypted JSON.
    # The encryption key is the value of the secret cookie. For security,
    # the value of the secret cookie (and hence the encryption key) is
    # intentionally not stored in the database.
    # Encryption prevents the tokens from being used even if
    # an attacker has a copy of the database.
    # The decrypted JSON contains at least
    # {access_token, refresh_token}.
    tokens_fernet = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    # The token is trusted without checking Amazon until update_ts,
    # which should be a short time after the last call to get user info.
    # Then we check the access token again.
    update_ts = Column(DateTime, nullable=False)
    # The token is no longer accepted after the expires time.
    expires = Column(DateTime, nullable=False)
    user_agent = Column(String, nullable=False)
    remote_addr = Column(String, nullable=False)
    username = Column(String, nullable=False)
    groups = Column(ARRAY(String), nullable=False)
    # id_claims contains the verified claims from the JWT id_token.
    id_claims = Column(JSONB, nullable=False)


# all_metadata_defined must be at the end of the file. It signals that
# all model classes have been defined successfully.
all_metadata_defined = True
