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

def block_ip(connection, ip):
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match(dl_type = 0x0800, nw_dst=ip)
    connection.send(msg)

def event_on_dnslookup(connection):
    # http://www.cavebear.com/archive/cavebear/Ethernet/type.html
    connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port = of.OFPP_CONTROLLER ),
                                       priority=1,
                                       match=of.ofp_match( dl_type=0x803C,
                                                           nw_dst=None)))
    # validate flow installed:
    # root@mininet-vm:/home/mininet# ovs-ofctl dump-flows s1


class BlacklistingLearningSwitch(LearningSwitch):

    def _handle_PacketIn(self, event):
        log.info(event.parsed)

        if isinstance(event.parsed, pkt.dns):
            log.info('DNS lookup occured')
            log.info('questions: %s', dns_packet.questions)
            log.info('answers: %s', dns_packet.answers)
            log.info('qr: %s', dns_packet.qr)

        postgresWrapper.is_on_blacklist('wikipedia.com') # TODO 

        super(BlacklistingLearningSwitch, self)._handle_PacketIn(event)

@poxutil.eval_args
def launch ():

    def _handle_ConnectionUp(event):
        connection = event.connection
        log.info("Connection %s" % (connection,))
        # example usage
        # block_ip(connection, "8.8.8.8")
        event_on_dnslookup(connection)
        BlacklistingLearningSwitch(connection, False)

    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)



class PostgresConnectionWrapper:
    def __init__(self):
        self.db_credentials = {
            'dbname': 'domain_blacklist',
            'user': 'domain_blacklist',
            'password': 'domain_blacklist',
            'host': 'localhost',
            'port': 5432
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