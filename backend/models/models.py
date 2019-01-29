from backend.models.meta import string_sequencer
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func
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


class User(Base):
    __tablename__ = 'user'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('user_seq'))
    wc_id = Column(
        String, nullable=False, index=True, unique=True)
    title = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    image_url = Column(String)

    @property
    def title(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Device(Base):
    __tablename__ = 'device'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('device_seq'))
    device_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(
        String, ForeignKey('user.id'), nullable=False)
    expo_token = Column(String)
    last_used = Column(DateTime, nullable=False, server_default=now_utc)
    os = Column(String)

    user = relationship(User)


class Design(Base):
    __tablename__ = 'design'
    id = Column(
        String, nullable=False, primary_key=True,
        server_default=string_sequencer('design_seq'))
    distribution_id = Column(String)
    wc_id = Column(String, nullable=False)
    title = Column(String)
    image_url = Column(String)
    wallet_url = Column(String)
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
    user_id = Column(
        String, ForeignKey('user.id'), nullable=False, index=True)
    created = Column(DateTime, nullable=False, server_default=now_utc)
    recipient = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default='pending')
    response = Column(String)

    user = relationship(User)


# all_metadata_defined must be at the end of the file. It signals that
# all model classes have been defined successfully.
all_metadata_defined = True
