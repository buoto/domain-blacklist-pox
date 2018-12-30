from models import Base, BlockedDomain
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Blacklist(object):
    def __init__(self):
        self.engine = create_engine('postgres:///domain_blacklist')
        self.sessionmaker = sessionmaker(bind=self.engine)

    def contains(self, domain):
        s = self.sessionmaker()
        return s.query(BlockedDomain)\
            .filter(BlockedDomain.name == domain).count() > 0

    def add(self, domain):
        s = self.sessionmaker()
        try:
            s.add(BlockedDomain(name=domain))
            s.commit()
        except:
            s.rollback()
            raise

    def remove(self, domain):
        s = self.sessionmaker()
        try:
            d = s.query(BlockedDomain)\
                .filter(BlockedDomain.name == domain).first()
            if d is None:
                return
            s.delete(d)
            s.commit()
        except:
            s.rollback()
            raise

    def domains(self):
        s = self.sessionmaker()
        return s.query(BlockedDomain).all()
