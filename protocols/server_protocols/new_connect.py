"""
Cancer OnConnect
"""
import uuid


class OnConnect:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x04'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    EVENT_TYPE = "on_connect"
    SENDING_HEADERS = 0

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        return int.from_bytes(message[1:2], 'big'), uuid.UUID(message[2:34].decode()), message[34:].decode(),

    @staticmethod
    def format_message(_message):
        """
        not used due to this being only a server command
        :param _message: nope
        :return:
        """
        return ''


class OnUDPConnect:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x04'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = str
    EVENT_TYPE = "on_udp_connect"
    SENDING_HEADERS = 0

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        return message[1:].decode(),

    @staticmethod
    def format_message(uuid_):
        """
        not used due to this being only a server command
        :param uuid_: the uuid of the connection
        :return:
        """
        return f'\x04{uuid_.hex}'.encode()


protocols = [OnConnect, OnUDPConnect]
