import netsquid as ns
from netsquid.protocols import NodeProtocol
from netsquid.nodes import Node
from netsquid.components.models import DelayModel
from netsquid.components import QuantumChannel, ClassicalChannel, Channel
from netsquid.nodes import DirectConnection
from netsquid.qubits import qubitapi as qapi
from netsquid.qubits.qubit import Qubit
from netsquid.components import QuantumMemory
import random

class PingPongDelayModel(DelayModel):
    def __init__(self, speed_of_light_fraction=0.5, standard_deviation=0.05):
        super().__init__()
        # (the speed of light is about 300,000 km/s)
        self.properties["speed"] = speed_of_light_fraction * 3e5
        self.properties["std"] = standard_deviation
        self.required_properties = ['length']  # in km

    def generate_delay(self, **kwargs):
        avg_speed = self.properties["speed"]
        std = self.properties["std"]
        # The 'rng' property contains a random number generator
        # We can use that to generate a random speed
        speed = self.properties["rng"].normal(avg_speed, avg_speed * std)
        delay = 1e9 * kwargs['length'] / speed  # in nanoseconds
        return delay

dist = 10
offset_dist = 1000
Alice = Node(name="Alice",port_names=['to_bob'])
Bob = Node(name="Bob",port_names=['from_alice'])

delay_model = PingPongDelayModel()

q_channel_AB = QuantumChannel(name="qchannel_AtoB",
                                length=dist/offset_dist)
#q_channel_BA = QuantumChannel(name="qchannel_BtoA",
#                                length=dist/offset_dist,delay=0)

#q_connection = DirectConnection(name='q_channel',
#                                    channel_AtoB=q_channel_AB,
#                                    channel_BtoA=q_channel_BA)

#channel_5 = Channel(name="cchannel[alice to bob]",
#                    length=dist/offset_dist,
#                    models={"delay_model": delay_model})
#channel_6 = Channel(name="cchannel[bob to alice]",
#                    length=dist/offset_dist,
#                    models={"delay_model": delay_model})
#
#connection = DirectConnection(name="conn[alice|bob]",
#                            channel_AtoB=channel_5,
#                            channel_BtoA=channel_6)
#
#Alice.connect_to(remote_node=Bob, connection=connection,
#                local_port_name="mixedIO", remote_port_name="mixedIO")

#Alice.connect_to(remote_node=Bob,connection=q_channel_AB,
#                local_port_name="q_tx_Alice",remote_port_name="q_rx_Bob")
#Bob.connect_to(remote_node=Alice,connection=q_channel_BA,
#                local_port_name="q_tx_Bob",remote_port_name="q_rx_Alice")

#print(Alice.ports)
#print(Bob.ports)

Alice.ports['to_bob'].connect(q_channel_AB.ports['send'])
Bob.ports['from_alice'].connect(q_channel_AB.ports['recv'])
qubit, = ns.qubits.create_qubits(1)
print(qubit)
Alice.ports["to_bob"].tx_output(qubit)
r_qubit = Bob.ports["from_alice"].rx_input()
stats = ns.sim_run(15)
print(r_qubit)
#while r_qubit == None:
#    r_qubit = Bob.ports["from_alice"].rx_input()
