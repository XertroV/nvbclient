from sqlalchemy import (
    Column,
    Index,
    Integer,
    LargeBinary,
    Text,
    BigInteger,
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


class UTXOs(Base):
    __tablename__ = 'utxos'
    id = Column(Integer, primary_key=True)
    tx_hash = Column(LargeBinary)
    tx_output_n = Column(Integer)
    script = Column(LargeBinary)
    value = Column(BigInteger)
    confirmations = Column(Integer)
    address = Column(Text, index=True)


Index('name_index', KeyStore.name, unique=True, mysql_length=255)
Index('utxos_conf', UTXOs.confirmations)
Index('utxos_hash_n', UTXOs.tx_hash, UTXOs.tx_output_n, unique=True)