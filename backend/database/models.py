from backend.database.meta import string_sequencer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    func,
    Unicode
)

from .meta import Base

now_utc = func.timezone('UTC', func.current_timestamp())


class SequenceKey(Base):
    """Contains the skip32 keys for generating sequences."""
    __tablename__ = 'sequence_key'
    seq_name = Column(
        String, primary_key=True, nullable=False)
    key_index = Column(
        Integer, primary_key=True, nullable=False, autoincrement=False)
    skip32_key = Column(BYTEA(10), nullable=False)


class MutableList(Mutable, list):
    """Allows operating on existing database arrays."""
    def add(self, value):
        """Move or add a value to the beginning of list, capping it at a
        certain number of elements.
        """
        if value in self:
            self.remove(value)
        self.insert(0, value)
        new_list = self[:8]
        self.clear()
        self.extend(new_list)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('customer_seq'))
    wc_id = Column(
        String, nullable=False, index=True, unique=True)
    title = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    profile_image_url = Column(String)
    recents = Column(
        MutableList.as_mutable(ARRAY(String)), nullable=False, default=[])
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
    device_id = Column(String, unique=True, nullable=False, index=True)
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
    original_line1 = Column(Unicode, nullable=False)
    original_line2 = Column(Unicode, nullable=True)
    original_city = Column(Unicode, nullable=False)
    original_state = Column(Unicode, nullable=False)
    original_zip_code = Column(Unicode, nullable=False)
    line1 = Column(Unicode, nullable=False)
    line2 = Column(Unicode, nullable=True)
    city = Column(Unicode, nullable=False)
    state = Column(Unicode, nullable=False)
    zip_code = Column(Unicode, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    downloaded = Column(DateTime, nullable=True)

# all_metadata_defined must be at the end of the file. It signals that
# all model classes have been defined successfully.
all_metadata_defined = True
