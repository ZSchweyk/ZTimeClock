from server import ThetaServer


server = ThetaServer("localhost")

try:
    for i in range(1000):
        server.send_to_radius_client(i)

    server.send_to_radius_client("Done")
finally:
    server.close_server()









# import enum
# from server_class import Webserver
# import pickle
#
#
# class PacketType(enum.Enum):
#     NULL = 0
#     COMMAND1 = 1
#     COMMAND2 = 2
#
#
# server = Webserver("localhost", 5001, PacketType)
# server.open_server()
# server.wait_for_connection()
#
# try:
#     for i in range(1000):
#         server.send_packet(PacketType.COMMAND2, pickle.dumps(i))
#
#     server.send_packet(PacketType.COMMAND2, pickle.dumps("Done"))
# finally:
#     server.close_connection()
#     server.close_server()
