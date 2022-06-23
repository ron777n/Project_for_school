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

    @staticmethod
    def get_message_data(message: bytes) -> Tuple[Any, ...]:
        """
        gets the packet_id color and data
        :param message:
        """
        packet_id = message[0]
        message_color = [x for x in message[1:4]]
        client_id = message[4]
        return packet_id, message_color, client_id, message[5:].decode()

    @staticmethod
    def format_message(message, color=(0, 0, 0)):
        """
        formats the message to send to the server
        :param message:
        :param color:
        :return:
        """
        return f"{ChatCommand.PACKET_ID.decode()}{''.join([x.to_bytes(1, 'little').decode() for x in color])}{message}"


protocols = [ChatCommand]
