"""
Sisyphus' python template.
EGG
"""
import socket
import threading
import time

from protocols import server_protocols
from Utils.events import event, post_event

IP = "127.0.0.1"
PORT = 7677


@event("on_message")
def user_message(message, colors, client_id):
    print(f"client with id({client_id}) sent: \"{message}\" with colors: {colors}")


@event("on_echo")
def echo(message):
    print("Echoed: ", message)


@event("on_echo")
def echo_message(message):
    print("Echoed message: ", message)


events = server_protocols.events
event_types = list(events.keys())


def receive_messages(socket_):
    """
    receives messages from the server
    """
    while 1:
        try:
            got = socket_.recv(1024)
        except socket.error:
            got = b""
        if not got:
            print("client Gone")
            return
        protocol = server_protocols.get_protocol(got)
        data = protocol.get_message_data(got)[1:]
        post_event(protocol.EVENT_TYPE, *data)


def main():
    """
    main function
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.recv(1024)
    receive_messages_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_messages_thread.start()
    while 1:
        msg = input("Enter a cancer: ")
        if msg[0].isdigit() and int(msg[0]) in range(len(server_protocols.protocols)):
            protocol = server_protocols.protocols[int(msg[0])]
            message = protocol.format_message(msg[1:])
        elif msg == "exit":
            break
        else:
            message = server_protocols.protocols[1].format_message(msg)
        if isinstance(message, str):
            message = message.encode()
        client_socket.sendall(message)
        time.sleep(2)


if __name__ == "__main__":
    main()
