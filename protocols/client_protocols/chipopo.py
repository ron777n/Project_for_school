"""
ImageMessage protocol
"""
from typing import Dict, List, Union


class ImageMessage:
    """
    simple echo protocol
    """
    PACKET_ID = b'\x05'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = bytes
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
        return socket_type == ImageMessage.SOCKET_TYPE and message[0] == ImageMessage.PACKET_ID[0] and len(
            message) > ImageMessage.HEADER_SIZE

    @staticmethod
    def get_answer(_headers: bytes, message: bytes, client_data: Dict[str, any],
                   clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param _headers: for the headers
        :param message: the message from the socket
        :param client_data: the data of the client
        :param clients: data of the clients
        :return: what to return to the client
        """
        for data in clients:
            if data["ID"] != client_data["ID"] and "user_name" in data:
                data["udp_message_queue"].put(ImageMessage.PACKET_ID + message)

        return ImageMessage.PACKET_ID + message

    @staticmethod
    def get_headers(message: bytes):
        """
        gets the headers for the protocol
        :param message: message
        :return: the headers
        """
        return ()


protocols = [ImageMessage]
