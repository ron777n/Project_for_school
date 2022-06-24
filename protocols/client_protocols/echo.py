"""
simple echo command, used for testing and as an example
"""
from typing import Dict, List, Union


class EchoCommand:
    """
    simple echo protocol
    """
    PACKET_ID = b'\x01'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    HEADER_SIZE = 1

    @staticmethod
    def match(message: bytes, socket_type: str, client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        return socket_type == EchoCommand.SOCKET_TYPE and message[0] == EchoCommand.PACKET_ID[0] and len(
            message) > EchoCommand.HEADER_SIZE

    @staticmethod
    def get_answer(headers: bytes, message: Union[str, bytes], client_data: Dict[str, any],
                   clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param headers: for the headers
        :param message: the message from the socket
        :param client_data: the data of the client
        :param clients: data of the clients
        :return: what to return to the client
        """
        return f"{EchoCommand.PACKET_ID.decode()}{message}"

    @staticmethod
    def get_headers(message: bytes):
        """
        gets the headers for the protocol
        :param message: message
        :return: the headers
        """
        return message[0], None


protocols = [EchoCommand]
