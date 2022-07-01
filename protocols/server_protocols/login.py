"""
Cancer SignUp
"""
import hashlib


class SignUp:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x02'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    EVENT_TYPE = "on_sign_up"
    SENDING_HEADERS = 2

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        return message[1:].decode(),

    @staticmethod
    def format_message(username, password):
        """
        formats the message to send to the server
        :return:
        """
        print(hashlib.md5(password.encode()).hexdigest())
        return f"{SignUp.PACKET_ID.decode()}{username.ljust(32)}{hashlib.md5(password.encode()).hexdigest()}"


class Login:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x03'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    EVENT_TYPE = "on_login"
    SENDING_HEADERS = 2

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        return int.from_bytes(message[1:3], "big"), message[3:36].decode(), message[36:].decode()

    @staticmethod
    def format_message(username, password):
        """
        formats the message to send to the server
        :return:
        """
        return f"{Login.PACKET_ID.decode()}{username.ljust(32)}{hashlib.md5(password.encode()).hexdigest()}"


protocols = [SignUp, Login]
