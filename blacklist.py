from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pox.lib.packet as pkt  # Packet parsing/construction
import pox.openflow.libopenflow_01 as of  # OpenFlow 1.0 library
from models import BlockedDomain, BlockedIP
from pox.core import core  # Main POX object
from pox.lib.addresses import IPAddr

LOG = core.getLogger()


def _get_traffic_to_ip_match(ip):
    return of.ofp_match(dl_type=pkt.ethernet.IP_TYPE, nw_dst=ip)


class Blacklist(object):
    def __init__(self):
        self.conns = set()
        self.engine = create_engine('postgres:///domain_blacklist')
        self.sessionmaker = sessionmaker(bind=self.engine)

    def contains(self, domain):
        session = self.sessionmaker()
        return session.query(BlockedDomain)\
            .filter(BlockedDomain.name == domain).count() > 0

    def add(self, domain):
        session = self.sessionmaker()
        try:
            session.add(BlockedDomain(name=domain))
            session.commit()
        except:
            session.rollback()
            raise

    def remove(self, domain):
        session = self.sessionmaker()
        try:
            domain = session.query(BlockedDomain)\
                .filter(BlockedDomain.name == domain).first()
            if domain is None:
                return
            session.delete(domain)
            session.commit()
            for ip in domain.ips:
                self._unblock_ip(IPAddr(ip.ip))
        except:
            session.rollback()
            raise


    def add_ip(self, domain, ip):
        session = self.sessionmaker()
        exists = session.query(BlockedDomain).filter(BlockedIP.ip == str(ip)).count() > 0
        if exists:
            return
        try:
            session.add(BlockedIP(domain=domain, ip=str(ip)))
            session.commit()
        except:
            session.rollback()
            raise

    def block(self, domain, ip):
        self.add_ip(domain, ip)
        self._block_ip(ip)

    def _block_ip(self, ip):
        msg = of.ofp_flow_mod()
        msg.match = _get_traffic_to_ip_match(ip)
        for conn in self.conns:
            conn.send(msg)

    def _unblock_ip(self, ip):
        msg = of.ofp_flow_mod()
        msg.command = of.OFPFC_DELETE_STRICT
        msg.match = _get_traffic_to_ip_match(ip)
        for conn in self.conns:
            conn.send(msg)

    def domains(self):
        session = self.sessionmaker()
        return session.query(BlockedDomain).all()

    def connection_up(self, conn):
        self.conns.add(conn)
        LOG.debug('new connection: %s', self.conns)

    def connection_down(self, conn):
        self.conns.discard(conn)
        LOG.debug('connection removed: %s', self.conns)
