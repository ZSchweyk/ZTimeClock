import enum
import pickle
from ServerPi.server_class import Server


class PacketType(enum.Enum):
    NULL = 0
    COMMAND1 = 1
    COMMAND2 = 2


class ThetaServer:
    def __init__(self, ip_address):
        #         |Bind IP       |Port |Packet enum
        self.s = Server(ip_address, 5001, PacketType)
        self.s.open_server()
        self.s.wait_for_connection()

    def send_to_radius_client(self, info):
        self.s.send_packet(PacketType.COMMAND2, pickle.dumps(info))

    def receive_from_radius_client(self):
        return pickle.loads(self.s.recv_packet()[1])

    def close_server(self):
        self.s.close_connection()
        self.s.close_server()


















