import netsquid as ns
from netsquid.protocols import NodeProtocol
from netsquid.nodes import Node
from netsquid.components.models import DelayModel
from netsquid.components import QuantumChannel, ClassicalChannel, Channel
from netsquid.nodes import DirectConnection
from netsquid.qubits import qubitapi as qapi
from netsquid.qubits.qubit import Qubit
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

class BB84Protocol(NodeProtocol):
    measurement_bases = [ns.X, ns.Z]
    def __init__(self, node):
        super().__init__(node)
        self.mutual_bits = []

    def run(self):
        if self.node.name == "Alice":
            self.alice_begin_cycle()
        while True:
            # Wait (yield) until input has arrived on our port:
            yield self.await_port_input(self.node.ports["mixedIO"])
            # Receive (RX) qubit on the port's input:
            message = self.node.ports["mixedIO"].rx_input()
            # print(f"{ns.sim_time():5.1f}: {message.items} received by {self.node.name}")
            if isinstance(message.items[0],Qubit):
                self.bob_receive_qubit(message.items[0])
            else:
                classical_message = message.items[0]
                if classical_message['type'] == 'bob_basis_confirm' and self.node.name == "Alice":
                    self.alice_confirm_basis(classical_message['content'])
                elif classical_message['type'] == 'alice_basis_confirm' and self.node.name == "Bob":
                    self.bob_end_cycle(classical_message['content'])
                elif classical_message['type'] == 'end_cycle' and self.node.name == "Alice":
                    self.alice_begin_cycle()
            # Send (TX) qubit to the other node via connection:
            # self.node.ports["mixedIO"].tx_output({'type':'Send back'})

    def alice_begin_cycle(self):
        qubit, = ns.qubits.create_qubits(1)
        self.bit = random.randrange(2)
        labels_basis = ("X", "Z")
        self.basis = labels_basis[random.randrange(2)]
        if self.bit == 0 and self.basis == "Z":
            # not doing anything
            pass
        elif self.bit == 1 and self.basis == "Z":
            qapi.operate(qubit, ns.X)
        elif self.bit == 0 and self.basis == "X":
            qapi.operate(qubit, ns.H)
        elif self.bit == 1 and self.basis == "X":
            qapi.operate(qubit, ns.X)
            qapi.operate(qubit, ns.H)
        self.node.ports["mixedIO"].tx_output(qubit)
    
    def bob_receive_qubit(self, qubit):
        basis = random.randrange(2)
        self.bit, _ = ns.qubits.measure(qubit, observable=self.measurement_bases[basis])
        labels_basis = ("X", "Z")
        self.basis = labels_basis[basis]
        self.node.ports["mixedIO"].tx_output({
            'type': 'bob_basis_confirm',
            'content': self.basis
        })
    
    def alice_confirm_basis(self, basis):
        if basis == self.basis:
            self.basis_confirm = True
            self.mutual_bits.append(self.bit)
            
        else:
            self.basis_confirm = False
        self.node.ports["mixedIO"].tx_output({
            'type': 'alice_basis_confirm',
            'content': self.basis_confirm
        })

    def bob_end_cycle(self, basis_confirm):
        if basis_confirm:
            self.mutual_bits.append(self.bit)
        self.node.ports["mixedIO"].tx_output({
            'type': 'end_cycle'
        })

class BB84KeyExchange():
    offset_dist = 1000 # default unit of length in channels is km
    def __init__(self, dist, ex_time, offset_time=1):
        self.offset_time = offset_time
        self.ex_time = ex_time
        node_alice = Node(name="Alice")
        node_bob = Node(name="Bob")

        delay_model = PingPongDelayModel()

        channel_5 = Channel(name="cchannel[alice to bob]",
                                length=dist/self.offset_dist,
                                models={"delay_model": delay_model})
        channel_6 = Channel(name="cchannel[bob to alice]",
                                length=dist/self.offset_dist,
                                models={"delay_model": delay_model})

        connection = DirectConnection(name="conn[alice|bob]",
                                    channel_AtoB=channel_5,
                                    channel_BtoA=channel_6)
                                    
        node_alice.connect_to(remote_node=node_bob, connection=connection,
                            local_port_name="mixedIO", remote_port_name="mixedIO")

        self.alice_protocol = BB84Protocol(node_alice)
        self.bob_protocol = BB84Protocol(node_bob)

    def run(self):
        ns.sim_reset()
        self.alice_protocol.start()
        self.bob_protocol.start()
        run_stats = ns.sim_run(duration=self.ex_time * self.offset_time)

        # print(self.alice_protocol.mutual_bits)
        # print(self.bob_protocol.mutual_bits)
        return len(self.bob_protocol.mutual_bits) / self.ex_time
