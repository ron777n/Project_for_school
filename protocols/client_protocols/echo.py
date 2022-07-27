"""
simple echo command, used for testing and as an example
"""
from typing import Dict, List, Union


class EchoTcpCommand:
    """
    simple echo protocol
    """
    PACKET_ID = b'\x01'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    HEADER_SIZE = 1

    @staticmethod
    def match(message: bytes, socket_type: str, _client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param _client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        return socket_type == EchoTcpCommand.SOCKET_TYPE and message[0] == EchoTcpCommand.PACKET_ID[0] and len(
            message) > EchoTcpCommand.HEADER_SIZE

    @staticmethod
    def get_answer(_headers, message: Union[str, bytes], _client_data: Dict[str, any],
                   _clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param _headers: for the headers
        :param message: the message from the socket
        :param _client_data: the data of the client
        :param _clients: data of the clients
        :return: what to return to the client
        """
        return f"{EchoTcpCommand.PACKET_ID.decode()}{message}"

    @staticmethod
    def get_headers(_message: bytes):
        """
        gets the headers for the protocol
        :param _message: message
        :return: the headers
        """
        return ()


class EchoUdpCommand:
    """
    simple echo protocol
    """
    PACKET_ID = b'\x01'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = str
    HEADER_SIZE = 1

    @staticmethod
    def match(message: bytes, socket_type: str, _client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param _client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        print(message, EchoUdpCommand.PACKET_ID[0])
        return socket_type == EchoUdpCommand.SOCKET_TYPE and message[0] == EchoUdpCommand.PACKET_ID[0] and len(
            message) > EchoUdpCommand.HEADER_SIZE

    @staticmethod
    def get_answer(_headers, message: Union[str, bytes], _client_data: Dict[str, any],
                   _clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param _headers: for the headers
        :param message: the message from the socket
        :param _client_data: the data of the client
        :param _clients: data of the clients
        :return: what to return to the client
        """
        return f"{EchoUdpCommand.PACKET_ID.decode()}{message}"

    @staticmethod
    def get_headers(_message: bytes):
        """
        gets the headers for the protocol
        :param _message: message
        :return: the headers
        """
        return ()


protocols = [EchoTcpCommand, EchoUdpCommand]
