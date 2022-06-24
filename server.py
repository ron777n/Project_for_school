"""
Sisyphus' python template.
EGG
"""
import queue
import socket
import select
import logging

from typing import Dict

from protocols.client_protocols import use_protocol

PORT = 7677


def main():
    """
    main function
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s:    %(levelname)s:    %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setblocking(False)
        try:
            server_socket.bind(("0.0.0.0", PORT))
        except socket.error:
            logger.error("Port: %d was taken by another program" % (PORT,))
            return
        server_socket.listen(5)

        inputs = [server_socket]
        clients: Dict[socket.socket: Dict[str: any]] = {}
        current_user = 0
        while inputs:
            outputs = filter(lambda x: not clients[x]["message_queue"].empty(), inputs[1:])
            readable, writeable, exceptional = select.select(inputs, outputs, inputs)
            for socket_ in readable:
                if socket_ is server_socket:
                    client_sock, client_address = server_socket.accept()
                    client_sock.setblocking(False)
                    logger.info(f"client connected from: {client_address[0]}")
                    inputs.append(client_sock)
                    clients[client_sock] = {"message_queue": queue.Queue(), "logged_in": True, "ID": current_user}
                    clients[client_sock]["message_queue"].put("egg")
                    current_user += 1
                    continue
                try:
                    msg = socket_.recv(1024)
                except ConnectionError:
                    msg = 0
                if not msg:
                    logger.warning(f"{socket_.getpeername()} sent invalid packet")
                    inputs.remove(socket_)
                    del clients[socket_]
                    socket_.close()
                    continue
                protocol_answer = use_protocol(msg, "TCP", clients[socket_], clients)
                clients[socket_]["message_queue"].put(protocol_answer)

            for socket_ in writeable:
                next_message = clients[socket_]["message_queue"].get_nowait()
                if isinstance(next_message, str):
                    next_message = next_message.encode()
                try:
                    socket_.sendall(next_message)
                except ConnectionError:
                    logger.warning(f"handling sending exception error for {socket_.getpeername()}")
                    inputs.remove(socket_)
                    del clients[socket_]
                    socket_.close()

            for socket_ in exceptional:
                logger.warning(f"handling exception error for {socket_.getpeername()}")
                inputs.remove(socket_)
                del clients[socket_]
                socket_.close()


if __name__ == "__main__":
    main()
