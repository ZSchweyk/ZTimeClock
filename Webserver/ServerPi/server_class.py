"""
This module contains the Webserver class that manages a dpea-p2p server.

General usage looks like this:

```
class PacketType(enum.Enum):
    NULL = 0
    COMMAND1 = 1
    COMMAND2 = 2

#         |Bind IP       |Port |Packet enum
s = Webserver("172.17.21.2", 5001, PacketType)
s.open_server()
s.wait_for_connection()

s.recv_packet() == (PacketType.COMMAND1, b"Hello!")
s.send_packet(PacketType.COMMAND2, b"Hello back!")

s.close_connection()
s.close_server()
```
"""
from ServerPi.common import *
import socket
import socketserver


class Server(object):
    """
    A class that manages the state of a listening dpea-p2p server.

    Upon calling .open_server(), it begins listening on the specified IP and port.
    .wait_for_connection() will wait for a connection from a client, allowing packets to be sent.

    .send_packet() and .recv_packet() allow for communication.

    When the connection is finished, call .close_connection().
    When the server is finished, call .close_server().
    """

    def __init__(self, bind_ip, port, packet_enum):
        """
        Initializes the server.

        :param bind_ip: The IP address to bind to.
        :param port: The port to bind to.
        :param packet_enum: The enum containing the packet types.
        :returns: A new Webserver object.
        """
        self.bind_ip = bind_ip
        self.port = port
        self.packet_enum = packet_enum

        self.server = None
        self.connection = None
        # socketserver.TCPServer.allow_reuse_address = True


    # Connection helpers

    def open_server(self):
        """
        Begins listening on bind_ip:port.
        """
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((self.bind_ip, self.port))
        self.server.listen(1)

    def wait_for_connection(self):
        """
        Waits for a connection from a client.
        This function will throw an error if a connection has previously been established.
        If _reconnection_ is desired, use .reconnect().

        :raises RuntimeError: If a connection has already been established.
        """
        if self.connection is not None:
            raise RuntimeError("A connection has already been established; use reconnect() to reconnect.")
        self.reconnect()

    def reconnect(self):
        """
        Waits for a connection from a client, regardless of any previous connections.
        """
        if self.connection is not None:
            try:
                self.close_connection()
            except OSError:
                pass
        conn, addr = self.server.accept()
        self.connection = conn

    def close_connection(self):
        """
        Closes the connection to the client.
        """
        self.connection.close()

    def close_server(self):
        """
        Closes the listening server.
        To reopen the server, call .open_server() again.
        """
        self.server.close()

    # Send/recv

    def send_packet(self, packet_type, payload):
        """
        Sends a packet to the client.

        :param packet_type: Either an int or an enum value representing the packet type.
        :param payload: The payload to be sent. Should be a bytes-like object.
        """
        send_packet(self.connection, packet_type, payload)

    def recv_packet(self):
        """
        Receives a packet from the client.

        :returns: A tuple of (packet_type, payload) from the server.
        """
        return recv_packet(self.connection, self.packet_enum)
