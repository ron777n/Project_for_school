"""
OnTcpConnection protocol
"""
from typing import Dict, List, Union


class OnTcpConnection:
    """
    simple echo protocol
    """
    PACKET_ID = b'\x04'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = bytes
    HEADER_SIZE = 0

    @staticmethod
    def match(message: bytes, socket_type: str, _client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param _client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        return socket_type == OnTcpConnection.SOCKET_TYPE and message[0] == OnTcpConnection.PACKET_ID[0] and len(
            message) > OnTcpConnection.HEADER_SIZE

    @staticmethod
    def get_answer(_headers: bytes, message: Union[str, bytes], _client_data: Dict[str, any],
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
        return f"{OnTcpConnection.PACKET_ID.decode()}{message}"

    @staticmethod
    def get_headers(message: bytes):
        """
        gets the headers for the protocol
        :param message: message
        :return: the headers
        """
        return ()


protocols = [OnTcpConnection]
