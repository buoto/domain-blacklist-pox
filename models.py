from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BlockedDomain(Base):
    __tablename__ = 'blocked_domain'
    name = Column(String, primary_key=True)

    def __str__(self):
        return self.name
