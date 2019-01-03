from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BASE = declarative_base()

class BlockedDomain(BASE):
    __tablename__ = 'blocked_domain'
    name = Column(String, primary_key=True)
    ips = relationship("BlockedIP", cascade="save-update, merge, delete")

    def __str__(self):
        return self.name


class BlockedIP(BASE):
    __tablename__ = 'blocked_ip'
    ip = Column(String, primary_key=True)
    domain = Column(String, ForeignKey('blocked_domain.name'))
