from sqlalchemy import (
    Column,
    Index,
    Integer,
    LargeBinary,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class KeyStore(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    encrypted = Column(LargeBinary)
    salt = Column(LargeBinary)
    address = Column(Text)

Index('name_index', KeyStore.name, unique=True, mysql_length=255)
