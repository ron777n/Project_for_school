"""
sends a message to the other players
"""


class ChatCommand:
    """
    Chat message protocol
    """
    PACKET_ID = b'\x0A'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    HEADER_SIZE = 4

    @staticmethod
    def match(message: bytes, socket_type: str, client_data) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param client_data: the data of the specified client
        :return:
        """
        return socket_type == ChatCommand.SOCKET_TYPE and message[0] == ChatCommand.PACKET_ID[0] and len(
            message) > ChatCommand.HEADER_SIZE and "user_name" in client_data

    @staticmethod
    def get_answer(headers, message, client_data, clients) -> str:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param headers: colours of the message
        :param message: the message from the socket
        :param client_data: the data of the client
        :param clients: data of the clients
        :return:
        """
        message_color = headers[0]

        msg_ = ChatCommand.format_message(message, client_data["ID"], message_color)
        for data in clients:
            if data["ID"] != client_data["ID"] and "user_name" in data:
                data["tcp_message_queue"].put(msg_)
        return msg_

    @staticmethod
    def get_headers(message: bytes):
        """
        Gets the headers of a message
        """
        message_color = [x for x in message[1:4]]
        return message_color,

    @staticmethod
    def format_message(message, player_id, color=(0, 0, 0)):
        """
        formats the message by the protocol
        :param message: the message to the client
        :param player_id: the player that sent the message
        :param color: the colour of the text
        :return: message by the protocol
        """
        return f"{ChatCommand.PACKET_ID.decode()}{''.join([x.to_bytes(1, 'little').decode() for x in color])}" \
               f"{player_id.to_bytes(2, 'big').decode()}{message}"


class UDPChatCommand:
    """
    Chat message protocol
    """
    PACKET_ID = b'\x0A'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = str
    HEADER_SIZE = 4

    @staticmethod
    def match(message: bytes, socket_type: str, client_data) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param client_data: the data of the specified client
        :return:
        """
        return message[0] == UDPChatCommand.PACKET_ID[0] and socket_type == UDPChatCommand.SOCKET_TYPE and len(
            message) > UDPChatCommand.HEADER_SIZE and "user_name" in client_data

    @staticmethod
    def get_answer(headers, message, client_data, clients) -> str:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param headers: colours of the message
        :param message: the message from the socket
        :param client_data: the data of the client
        :param clients: data of the clients
        :return:
        """
        message_color = headers[0]

        msg_ = UDPChatCommand.format_message(message, client_data["ID"], message_color)
        for data in clients:
            if data["ID"] != client_data["ID"] and "user_name" in data:
                data["udp_message_queue"].put(msg_)
        return msg_

    @staticmethod
    def get_headers(message: bytes):
        """
        Gets the headers of a message
        """
        message_color = [x for x in message[1:4]]
        return message_color,

    @staticmethod
    def format_message(message, player_id, color=(0, 0, 0)):
        """
        formats the message by the protocol
        :param message: the message to the client
        :param player_id: the player that sent the message
        :param color: the colour of the text
        :return: message by the protocol
        """
        print(color)
        return f"{UDPChatCommand.PACKET_ID.decode()}{''.join([x.to_bytes(1, 'little').decode() for x in color])}" \
               f"{player_id.to_bytes(2, 'big').decode()}{message}"


protocols = [ChatCommand, UDPChatCommand]
