"""
for when someone sends a message to everyone
"""
from typing import Any, Tuple


class ChatCommand:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x0A'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    EVENT_TYPE = "on_message"
    SENDING_HEADERS = 1

    @staticmethod
    def get_message_data(message: bytes) -> Tuple[Any, ...]:
        """
        gets the packet_id color and data
        :param message:
        """
        message_color = [x for x in message[1:4]]
        client_id = int.from_bytes(message[4:6], "big")
        return message_color, client_id, message[6:].decode()

    @staticmethod
    def format_message(message, color=(0, 0, 0)):
        """
        formats the message to send to the server
        :param message:
        :param color:
        :return:
        """
        print(message, color)
        return f"{ChatCommand.PACKET_ID.decode()}{''.join([x.to_bytes(1, 'little').decode() for x in color])}{message}"


class UDPChatCommand:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x0A'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = str
    EVENT_TYPE = "on_udp_message"
    SENDING_HEADERS = 1

    @staticmethod
    def get_message_data(message: bytes) -> Tuple[Any, ...]:
        """
        gets the packet_id color and data
        :param message:
        """
        message_color = [x for x in message[1:4]]
        client_id = int.from_bytes(message[4:6], "big")
        return message_color, client_id, message[6:].decode()

    @staticmethod
    def format_message(message, color=(0, 0, 0)):
        """
        formats the message to send to the server
        :param message:
        :param color:
        :return:
        """
        return f"{ChatCommand.PACKET_ID.decode()}{''.join([x.to_bytes(1, 'little').decode() for x in color])}{message}"


protocols = [ChatCommand, UDPChatCommand]
