"""
handles the connection with the server, at least in the basics
"""
import socket
import threading
import loader
from Utils.events import post_event, create_event, subscribe

server_protocols = loader.Load("protocols/server_protocol", "protocols/server_protocols")
server_protocols.load_modules()

IP = "127.0.0.1"
TCP_PORT = 7678
UDP_PORT = 7676

for event_ in server_protocols.data["events"]:
    create_event(event_)

protocols = server_protocols.data["protocols"]


class Client:
    """
    the client class
    """
    def __init__(self, ):
        self.connected = False
        subscribe("on_connect", self.on_connect)
        self.data = {}
        self.client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_tcp_socket.connect((IP, TCP_PORT))
        except socket.error:
            raise ConnectionError("Server dead")

        self.client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        receive_udp_messages_thread = threading.Thread(target=self.receive_messages,
                                                       args=(self.client_udp_socket, "UDP"), daemon=True)
        receive_udp_messages_thread.start()

        receive_tcp_messages_thread = threading.Thread(target=self.receive_messages,
                                                       args=(self.client_tcp_socket, "TCP"), daemon=True)
        while "udp_socket" not in self.data:
            pass  # waits for udp socket to connect
        receive_tcp_messages_thread.start()
        while not self.connected:
            pass

    def on_connect(self, _data, client_id, client_uuid):
        """
        saves the information of the client and tries to connect the udp socket
        :return:
        """
        self.data["ID"] = client_id
        self.data["UUID"] = client_uuid
        message = protocols["OnUDPConnect"].format_message(client_uuid)
        message_length = len(message) + 3
        message = message_length.to_bytes(3, "big") + message
        while "udp_socket" not in self.data:
            pass
        self.data["udp_socket"].sendto(message, (IP, UDP_PORT))
        self.connected = True


    def receive_messages(self, socket_: socket.socket, socket_type):
        """
        receives messages from the server
        """
        if socket_type == "TCP":
            receive = lambda: socket_.recv(1024)
        elif socket_type == "UDP":
            socket_.bind((IP, 0))
            self.data["udp_socket"] = socket_
            receive = lambda: socket_.recvfrom(65_535)[0]
        else:
            return "?!?!"
        while 1:
            message = b""
            message_length = 1
            while len(message) < message_length:
                try:
                    got = receive()
                except socket.error as e:
                    print(f"FUCK {e} for {socket_type}")
                    got = b""
                if not got:
                    print("client Gone")
                    return
                message += got
                message_length = int.from_bytes(message[:3], "big")
            message = message[3:]
            # print(message)
            protocol = server_protocols.use_protocol(message, socket_type)
            if not protocol:
                print(f"no protocol found for {message}")
                continue
            message_data = protocol.get_message_data(message)
            if not message_data:
                post_event(protocol.EVENT_TYPE)
            *headers, data_ = message_data
            post_event(protocol.EVENT_TYPE, data_, *headers)

    def send(self, protocol, protocol_answer):
        """
        sends a message to the server
        :param protocol: the protocol or whether or not it's tcp
        :param protocol_answer: what the protocol answered
        :return:
        """
        if not protocol_answer:
            return "Egg"

        if isinstance(protocol_answer, str):
            protocol_answer = protocol_answer.encode()

        message_length = len(protocol_answer) + 3
        protocol_answer = message_length.to_bytes(3, "big") + protocol_answer
        if protocol == "TCP" or protocol.SOCKET_TYPE == "TCP":
            self.client_tcp_socket.sendall(protocol_answer)
        else:
            self.client_udp_socket.sendto(protocol_answer, (IP, UDP_PORT))

