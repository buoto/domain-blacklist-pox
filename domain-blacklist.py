# Import some POX stuff
import pox.lib.packet as pkt  # Packet parsing/construction
import pox.lib.recoco as recoco  # Multitasking library
import pox.lib.revent as revent  # Event library
import pox.lib.util as poxutil  # Various util functions
import pox.openflow.libopenflow_01 as of  # OpenFlow 1.0 library
from blacklist import Blacklist
from handler import BlacklistHandler
from models import Base
from pox.core import core  # Main POX object
from pox.forwarding.l2_learning import LearningSwitch
from pox.lib.addresses import EthAddr, IPAddr  # Address types
from pox.web import webcore

# Create a logger for this component
log = core.getLogger()

blacklist = Blacklist()

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
                is_banned = blacklist.contains(domain)
                is_a = answer.qtype == answer.A_TYPE
                if is_banned and is_a:
                    ip = answer.rddata
                    log.info("Blocking ip {} of blacklisted domain {}".format(ip, domain))
                    blacklist.block(domain, ip)

        super(BlacklistingLearningSwitch, self)._handle_PacketIn(event)


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
    core.WebServer.set_handler("/blacklist", BlacklistHandler, {'blacklist': blacklist})
    def _handle_ConnectionUp(event):
        connection = event.connection
        blacklist.connection_up(connection)
        log.info("Connection %s" % (connection,))
        BlacklistingLearningSwitch(connection, False)

    def _handle_ConnectionDown(event):
        connection = event.connection
        blacklist.connection_down(connection)

    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("ConnectionDown", _handle_ConnectionDown)
