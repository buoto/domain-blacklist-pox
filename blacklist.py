from pox.core import core  # Main POX object
import pox.openflow.libopenflow_01 as of  # OpenFlow 1.0 library
from pox.lib.addresses import IPAddr
import pox.lib.packet as pkt  # Packet parsing/construction
from models import BlockedDomain, BlockedIP
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

log = core.getLogger()

class Blacklist(object):
    def __init__(self):
        self.conns = set()
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
            for ip in d.ips:
                self._unblock_ip(IPAddr(ip.ip))
        except:
            s.rollback()
            raise


    def add_ip(self, domain, ip):
        s = self.sessionmaker()
        exists = s.query(BlockedDomain).filter(BlockedIP.ip == str(ip)).count() > 0
        if exists:
            return
        try:
            s.add(BlockedIP(domain=domain, ip=str(ip)))
            s.commit()
        except:
            s.rollback()
            raise

    def block(self, domain, ip):
        self.add_ip(domain, ip)
        self._block_ip(ip)

    def _block_ip(self, ip):
        msg = of.ofp_flow_mod()
        msg.match = self.get_traffic_to_ip_match(ip)
        for conn in self.conns:
            conn.send(msg)

    def _unblock_ip(self, ip):
        msg = of.ofp_flow_mod()
        msg.command = of.OFPFC_DELETE_STRICT
        msg.match = self.get_traffic_to_ip_match(ip)
        for conn in self.conns:
            conn.send(msg)

    def get_traffic_to_ip_match(self, ip):
        return of.ofp_match(dl_type = pkt.ethernet.IP_TYPE, nw_dst=ip)

    def domains(self):
        s = self.sessionmaker()
        return s.query(BlockedDomain).all()

    def connection_up(self, conn):
        self.conns.add(conn)
        log.debug('new connection: %s', self.conns)

    def connection_down(self, conn):
        self.conns.discard(conn)
        log.debug('connection removed: %s', self.conns)
