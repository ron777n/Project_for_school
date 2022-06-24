"""
for testing and as an example
"""


class EchoCommand:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x01'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    EVENT_TYPE = "on_echo"

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        packet_id = message[0]
        return packet_id, message[1:].decode()

    @staticmethod
    def format_message(message):
        """
        formats the message to send to the server
        :param message: message to send
        :return:
        """
        return f"{EchoCommand.PACKET_ID.decode()}{message}"


protocols = [EchoCommand]
