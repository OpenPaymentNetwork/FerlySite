from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .meta import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    wc_id = Column(
        String, nullable=False, index=True, unique=True)
    title = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    expo_token = Column(String)
    image_url = Column(String)

    @property
    def title(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Device(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    device_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(
        Integer, ForeignKey('user.id'), nullable=False, index=True)

    user = relationship(User)


class Design(Base):
    __tablename__ = 'design'
    id = Column(Integer, primary_key=True)
    distribution_id = Column(String)
    wc_id = Column(String, nullable=False)
    title = Column(String)
    image_url = Column(String)
    wallet_url = Column(String)


class Contact(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)


Index('user_index', User.wc_id, unique=True, mysql_length=255)
