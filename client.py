"""
Sisyphus' python template.
EGG
"""
import socket
import threading
import time

# from decorators import print_log

import loader
from Utils.events import event, post_event, create_event

# from decorators import print_log

server_protocols = loader.Load("protocols/server_protocol", "protocols/server_protocols")
server_protocols.load_modules()

IP = "127.0.0.1"
TCP_PORT = 7678
UDP_PORT = 7676

for event_ in server_protocols.data["events"]:
    create_event(event_)

protocols = server_protocols.data["protocols"]
protocols_names = list(server_protocols.data["protocols"].values())
print("protocols:",
      *[f"{protocol_name}: {index}" for index, protocol_name in enumerate(server_protocols.data["protocols"]) if
        "Connect" not in protocol_name], sep="\n")  # just to print the protocols for the menu


@event("on_message")
def user_message(message, colors, client_id):
    """
    simple example of using an event
    :param message:
    :param colors:
    :param client_id:
    """
    print(f"client with id({client_id}) sent: \"{message}\" with colors: {colors}")


@event("on_sign_up")
def sign_up(message):
    """
    checks and prints if logged in
    :param message: message of log in or user exists
    """
    print(f"sign_up returned - {message}")


@event  # made it so that if it didn't get anything the function uses the function name as type, because i fuckin' can
def on_echo(message):
    """
    simple example of using an event
    :param message:
    """
    print("Echoed:", message)


@event("on_echo_udp")
def echo_udp(message):
    """
    simple example of using an event for udp
    :param message:
    """
    print("Echoed from udp socket:", message)


@event("on_login")
def login_event(_url, client_id, user_name):
    """
    prints if logged in
    :param _url: later add url to skins
    :param client_id: id of the client that logged in, 0 if login failed
    :param user_name: user name of the person, message of fail if login failed
    """
    if not client_id:
        print("login failed", user_name + _url)
        return
    elif client_id == data["ID"]:
        print(f"successfully logged in as {user_name}")
        data["user_name"] = user_name
    else:
        print(f"client with id({client_id}) logged in as {user_name}")


@event("on_connect")
def on_connect(_data, client_id, client_uuid):
    """
    saves the information of the client and tries to connect the udp socket
    :return:
    """
    data["ID"] = client_id
    data["UUID"] = client_uuid
    print(client_uuid)
    data["udp_socket"].sendto(protocols["OnUDPConnect"].format_message(client_uuid), (IP, UDP_PORT))


@event("on_udp_connect")
def on_udp_connect(confirm_message):
    """
    prints that the udp socket connected, or not
    :return:
    """
    print(confirm_message)


@event("on_udp_message")
def on_udp_message(message, colors, client_id):
    """
    to test something as cancer as this
    :param message:
    :param colors:
    :param client_id:
    """
    print(f"client with id({client_id}) sent: \"{message}\" with colors: {colors}, from a udp socket, wow")


def receive_messages(socket_: socket.socket, socket_type):
    """
    receives messages from the server
    """
    if socket_type == "TCP":
        receive = lambda: socket_.recv(1024)
    elif socket_type == "UDP":
        socket_.bind((IP, 0))
        data["udp_socket"] = socket_
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
        protocol = server_protocols.use_protocol(message, socket_type)
        if not protocol:
            print(f"no protocol found for {message}")
            continue
        message_data = protocol.get_message_data(message)
        if not message_data:
            post_event(protocol.EVENT_TYPE)
        *headers, data_ = message_data
        post_event(protocol.EVENT_TYPE, data_, *headers)


data = {}


def main():
    """
    main function
    """
    client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_tcp_socket.connect((IP, TCP_PORT))

    receive_udp_messages_thread = threading.Thread(target=receive_messages, args=(client_udp_socket, "UDP"))
    receive_udp_messages_thread.setDaemon(True)
    receive_tcp_messages_thread = threading.Thread(target=receive_messages, args=(client_tcp_socket, "TCP"))
    receive_tcp_messages_thread.setDaemon(True)

    receive_udp_messages_thread.start()
    while "udp_socket" not in data:
        pass
    receive_tcp_messages_thread.start()
    while 1:
        time.sleep(1)
        protocol = None
        msg = input("Enter a cancer: ")
        if msg == "exit":
            break
        if msg in protocols:
            protocol = protocols[msg]
        elif msg.isnumeric() and int(msg) in range(len(protocols_names)):
            protocol = protocols_names[int(msg)]
        if not protocol:
            protocol = protocols["EchoCommand"]
            headers = [msg]
        else:
            headers = [input("enter header: ") for _ in range(protocol.SENDING_HEADERS)]

        message = protocol.format_message(*headers)
        socket_type = protocol.SOCKET_TYPE

        if not message:
            continue

        if isinstance(message, str):
            message = message.encode()

        message_length = len(message) + 3
        message = message_length.to_bytes(3, "big") + message
        if socket_type == "TCP":
            client_tcp_socket.sendall(message)
        else:
            client_udp_socket.sendto(message, (IP, UDP_PORT))


if __name__ == "__main__":
    main()
