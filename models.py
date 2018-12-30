from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BlockedDomain(Base):
    __tablename__ = 'blocked_domain'
    name = Column(String, primary_key=True)
    ips = relationship("BlockedIP", cascade="save-update, merge, delete")

    def __str__(self):
        return self.name


class BlockedIP(Base):
    __tablename__ = 'blocked_ip'
    ip = Column(String, primary_key=True)
    domain = Column(String, ForeignKey('blocked_domain.name'))
