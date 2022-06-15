"""
This module contains helper functions for parsing packets.
It should only be used internally in general, but is available in case special circumstances arise.
"""
import struct


PORT = 5001

HEADER_FORMAT = "<II"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def get_value(obj):
    """
    Helper for converting an object that is either an int or an enum to an int.

    :param obj: Either an int or an enum object.
    :returns: An int corresponding to the input.
    """
    if isinstance(obj, int):
        return obj
    else:
        return obj.value

# Packet helpers

def create_header(packet_type, payload_len):
    """
    Create a packet header with type packet_type and payload length payload_len.

    :param packet_type: Either an int or an enum value representing the packet type.
    :param payload_len: The length of the payload that will be attached to this header.
    :returns: A bytes object containing the header.
    """
    return struct.pack(HEADER_FORMAT, get_value(packet_type), payload_len)

def create_packet(packet_type, payload):
    """
    Create a packet with type packet_type and the payload as given.

    :param packet_type: Either an int or an enum value representing the packet type.
    :param payload: The payload to be sent. Should be a bytes-like object.
    :returns: The packet in a bytes-like object.
    """
    header = create_header(packet_type, len(payload))
    data = header + payload
    return data

def send_packet(sock, packet_type, payload):
    """
    Send a complete packet over sock with type packet_type and the payload as given.

    :param sock: The socket on which to send the packet.
    :param packet_type: Either an int or an enum value representing the packet type.
    :param payload: The payload to be sent. Should be a bytes-like object.
    """
    sock.sendall(create_packet(packet_type, payload))


# Unpacket helpers

def read_header(data, packet_enum):
    """
    Parse a packet header from data of the correct length, interpreting types via packet_enum.

    :param data: The from which to read the header. Must be the correct length.
    :param packet_enum: The enum containing the packet types.
    :returns: A tuple of (packet_type, payload_len)
    """
    if len(data) != HEADER_SIZE:
        raise ValueError("data size was %d, but expected %d" % (len(data), HEADER_SIZE))
    raw_type, payload_len = struct.unpack(HEADER_FORMAT, data)
    packet_type = packet_enum(raw_type)
    return packet_type, payload_len

def read_packet(data, packet_enum):
    """
    Parse a packet from data of the correct length, interpreting types via packet_enum.

    The expected length is calculated as HEADER_SIZE + payload_len.

    :param data: The from which to read the header and payload. Must be the correct length.
    :param packet_enum: The enum containing the packet types.
    :returns: A tuple of (packet_type, payload)
    """
    if len(data) < HEADER_SIZE:
        raise ValueError("data size was %d, but expected at least %d" % (len(data), HEADER_SIZE))
    packet_type, payload_len = read_header(data[:HEADER_SIZE], packet_enum)
    expected_size = HEADER_SIZE + payload_len
    if len(data) != expected_size:
        raise ValueError("data size was %d, but expected %d" % (len(data), expected_size))
    return packet_type, data[HEADER_SIZE:]

def _recvn(sock, l):
    """
    Receive exactly l bytes over sock.

    :param sock: The socket on which to receive.
    :param l: The number of bytes to receive.
    :returns: l bytes from the socket.
    """
    buf = b""
    while len(buf) < l:
        buf += sock.recv(l - len(buf))
    return buf

def recv_packet(sock, packet_enum):
    """
    Receive a complete packet over sock, with types determine by packet_enum.

    :param sock: The socket on which to receive.
    :param packet_enum: The enum containing the packet types.
    :returns: A tuple of (packet_type, payload)
    """
    header = _recvn(sock, HEADER_SIZE)
    packet_type, payload_len = read_header(header, packet_enum)
    payload = _recvn(sock, payload_len)
    return read_packet(header + payload, packet_enum)
