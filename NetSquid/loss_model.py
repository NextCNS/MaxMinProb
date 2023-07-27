from netsquid.components.models.qerrormodels import FibreLossModel
from netsquid.components.qchannel import QuantumChannel
loss_model = FibreLossModel(p_loss_init=0.83,p_loss_length=0.2)
qchannel = QuantumChannel("MyQChannel",length=20,models={'quantum_loss_model':loss_model})
