# Copyright 2013 <Your Name Here>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A skeleton POX component

You can customize this to do whatever you like.  Don't forget to
adjust the Copyright above, and to delete the Apache license if you
don't want to release under Apache (but consider doing so!).

Rename this file to whatever you like, .e.g., mycomponent.py.  You can
then invoke it with "./pox.py mycomponent" if you leave it in the
ext/ directory.

Implement a launch() function (as shown below) which accepts commandline
arguments and starts off your component (e.g., by listening to events).

Edit this docstring and your launch function's docstring.  These will
show up when used with the help component ("./pox.py help --mycomponent").
"""

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
