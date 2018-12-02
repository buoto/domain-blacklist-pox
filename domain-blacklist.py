# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
import pox.lib.packet as pkt                  # Packet parsing/construction
from pox.lib.addresses import EthAddr, IPAddr # Address types
import pox.lib.util as poxutil                # Various util functions
import pox.lib.revent as revent               # Event library
import pox.lib.recoco as recoco               # Multitasking library
from pox.forwarding.l2_learning import LearningSwitch

# Create a logger for this component
log = core.getLogger()


def dns_response_match():
    match = of.ofp_match()
    match.dl_type = pkt.ethernet.IP_TYPE
    match.nw_proto = pkt.ipv4.UDP_PROTOCOL
    match.tp_src = pkt.dns.SERVER_PORT
    return match


class BlacklistingLearningSwitch(LearningSwitch):

    def __init__(self, connection, *args, **kwargs):
        super(BlacklistingLearningSwitch, self).__init__(connection, *args, **kwargs)
        self.notify_on_dnslookup()

    def _handle_PacketIn(self, event):
        dns_packet = event.parsed.find('dns')
        if dns_packet:
            for answer in dns_packet.answers:
                domain = answer.name
                is_banned = postgresWrapper.is_on_blacklist(domain)
                is_a = answer.qtype == answer.A_TYPE
                if is_banned and is_a:
                    ip = answer.rddata
                    log.info("Blocking ip {} of blacklisted domain {}".format(ip, domain))
                    self.block_ip(ip)

        super(BlacklistingLearningSwitch, self)._handle_PacketIn(event)

    def block_ip(self, ip):
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match(dl_type = pkt.ethernet.IP_TYPE, nw_dst=ip)
        self.connection.send(msg)

    def notify_on_dnslookup(self):
        log.info("Installing dns response capturing flow")
        msg = of.ofp_flow_mod()
        msg.match = dns_response_match()
        msg.priority = 99
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        self.connection.send(msg)
        # validate flow installed:
        # root@mininet-vm:/home/mininet# ovs-ofctl dump-flows s1

@poxutil.eval_args
def launch ():

    def _handle_ConnectionUp(event):
        connection = event.connection
        log.info("Connection %s" % (connection,))
        # example usage
        # block_ip(connection, "8.8.8.8")
        BlacklistingLearningSwitch(connection, False)

    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)



class PostgresConnectionWrapper:
    def __init__(self):
        self.db_credentials = {
            'dbname': 'domain_blacklist',
        }
    
    def is_on_blacklist(self, domainName):
        import psycopg2
        try:
            with psycopg2.connect(**self.db_credentials) as conn, conn.cursor() as cur:
                cur.execute('SELECT count(*) from banned_domain where domain = (%s)' ,[domainName])
                rows = cur.fetchall()
                is_blacklisted = rows[0][0] > 0
                if is_blacklisted:
                    log.debug('Domain ' + domainName + ' on blacklist')
                else:
                    log.debug('Domain ' + domainName + ' is accessible')
                return is_blacklisted
        except psycopg2.ProgrammingError as e:
            log.info('Exception occured')
            log.error(e)
            conn.tpc_rollback()
        return False

postgresWrapper = PostgresConnectionWrapper()
