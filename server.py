"""
Sisyphus' python template.
EGG
"""
import queue
import socket
import select
import logging
import uuid


from typing import Dict, List, Tuple

import loader


class Server:
    """
    everything server
    """
    TCP_PORT = 7678
    UDP_PORT = 7676

    def __init__(self, ):
        self.Server_protocol = loader.Load("protocols/client_protocol", "protocols/client_protocols")
        self.Server_protocol.load_modules()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(stream_handler)
        self.clients: Dict[socket.socket: Dict[str: any]] = {}
        self.udp_clients: Dict[Tuple[str, int]: Dict[str: any]] = {}
        self.inputs: List[socket.socket] = []

    def main_loop(self):
        """
        the main loop of the server
        :return:
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_TCP_socket:
            server_TCP_socket.setblocking(False)
            try:
                server_TCP_socket.bind(("0.0.0.0", Server.TCP_PORT))
            except socket.error:
                self.logger.critical("Port: %d was taken by another program" % (Server.TCP_PORT,))
                return
            server_TCP_socket.listen(5)

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_UDP_socket:
                try:
                    server_UDP_socket.bind(("0.0.0.0", Server.UDP_PORT))
                except socket.error:
                    self.logger.critical("Port: %d was taken by another program" % (Server.UDP_PORT,))
                    return

                self.inputs.extend([server_TCP_socket, server_UDP_socket])
                current_user = 1
                while self.inputs:
                    outputs = filter(lambda x: not self.clients[x]["tcp_message_queue"].empty(), self.inputs[2:])
                    readable, writeable, exceptional = select.select(self.inputs, outputs, self.inputs)

                    # if any([readable, writeable, exceptional]):
                    #     print(len(readable), len(writeable), len(exceptional))

                    for socket_ in readable:
                        if socket_ is server_TCP_socket:
                            client_sock, client_address = server_TCP_socket.accept()
                            client_sock.setblocking(False)
                            self.logger.info(f"client connected from: {client_address[0]}")
                            self.inputs.append(client_sock)
                            client_uuid = uuid.uuid4()
                            self.clients[client_sock] = {"tcp_message_queue": queue.Queue(),
                                                         "ID": current_user, "UUID": client_uuid, 'msg': b''}
                            self.clients[client_sock]["tcp_message_queue"].put(b'\x04' + current_user.to_bytes(1, 'big')
                                                                               + client_uuid.hex.encode())
                            current_user += 1
                            continue
                        elif socket_ is server_UDP_socket:
                            message, address = server_UDP_socket.recvfrom(65_535)
                            message = message[3:]
                            if address not in self.udp_clients:
                                client_uuid = uuid.UUID(message[1:].decode())
                                for data in self.clients.values():
                                    if client_uuid == data["UUID"]:
                                        data["udp_socket"] = address
                                        data["udp_message_queue"] = queue.Queue()
                                        self.udp_clients[address] = data
                                        protocol_answer = f'\x04Successfully connected udp socket to tcp data'.encode()
                                        break
                                else:
                                    protocol_answer = f'\x04No client found for that UUID'.encode()
                                message = (len(protocol_answer)+3).to_bytes(3, "big") + protocol_answer
                                server_UDP_socket.sendto(message, address)
                                continue
                            protocol_answer = self.Server_protocol.use_protocol(message, "UDP",
                                                                                self.udp_clients[address], self.clients)
                            if isinstance(protocol_answer, str):
                                protocol_answer = protocol_answer.encode()
                            self.clients[client_sock]["udp_message_queue"].put(protocol_answer)
                            continue
                        try:
                            msg = socket_.recv(1024)
                        except ConnectionError:
                            msg = ''
                        if not msg:
                            self.logger.info(f"{socket_.getpeername()} sent invalid packet")
                            self.remove_client(socket_)
                            continue
                        if not self.clients[socket_]["msg"]:
                            msg_length, msg = int.from_bytes(msg[:3], 'big'), msg[3:]
                            self.clients[socket_]["message_length"] = msg_length - 3
                        if len(msg) < self.clients[socket_]["message_length"]:
                            self.clients[socket_]["msg"] += msg
                            if len(self.clients[socket_]["msg"]) < self.clients[socket_]["message_length"]:
                                continue
                            msg = self.clients[socket_]["msg"]
                        protocol_answer = self.Server_protocol.use_protocol(msg, "TCP",
                                                                            self.clients[socket_], self.clients)
                        self.clients[socket_]["tcp_message_queue"].put(protocol_answer)
                        self.clients[socket_]['msg'] = b''

                    for socket_ in writeable:
                        next_message = self.clients[socket_]["tcp_message_queue"].get_nowait()
                        if isinstance(next_message, str):
                            next_message = next_message.encode()
                        message_length = len(next_message) + 3
                        message = message_length.to_bytes(3, "big") + next_message
                        try:
                            socket_.sendall(message)
                        except ConnectionError:
                            self.logger.info(f"handling sending exception error for {socket_.getpeername()}")
                            self.remove_client(socket_)

                    for socket_ in exceptional:
                        self.logger.info(f"handling exception error for {socket_.getpeername()}")
                        self.remove_client(socket_)

                    writeable_udp = True
                    while writeable_udp:
                        writeable_udp = list(filter(lambda x: not self.udp_clients[x]["udp_message_queue"].empty(),
                                                    self.udp_clients))
                        for address in writeable_udp:
                            next_message = self.udp_clients[address]["udp_message_queue"].get_nowait()
                            if isinstance(next_message, str):
                                next_message = next_message.encode()
                            message_length = len(next_message) + 3
                            message = message_length.to_bytes(3, "big") + next_message
                            try:
                                socket_.sendto(message, address)
                            except ConnectionError as e:
                                self.logger.warning(f"sending error({e}), socket: {socket_.getpeername()} "
                                                    f"for message: {message}")

    def remove_client(self, client_socket):
        """
        removes a tcp client
        :param client_socket:
        """
        self.inputs.remove(client_socket)
        if "udp_socket" in self.clients[client_socket]:
            del self.udp_clients[self.clients[client_socket]["udp_socket"]]
        del self.clients[client_socket]
        client_socket.close()


def main():
    """
    main function
    """
    server = Server()
    server.main_loop()


if __name__ == "__main__":
    main()
