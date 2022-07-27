"""
SignUp protocol
"""
from typing import Dict, List, Union
import json


class SignUp:
    """
    creates a new client
    """
    PACKET_ID = b'\x02'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    HEADER_SIZE = 65

    @staticmethod
    def match(message: bytes, socket_type: str, client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        return socket_type == SignUp.SOCKET_TYPE and message[0] == SignUp.PACKET_ID[
            0] and "user_name" not in client_data and len(message) >= SignUp.HEADER_SIZE

    @staticmethod
    def get_answer(headers, message: Union[str, bytes], _client_data: Dict[str, any],
                   _clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param headers: requested name and password(in md5hash)
        :param message: url of the skin to use, because i can
        :param _client_data: the data of the client
        :param _clients: data of the clients
        :return: what to return to the client
        """
        name, password = headers
        with open("users.json", "r+") as f:
            data: dict = json.load(f)  # TODO change this to firebase or other cloud service
            if name in data["users"]:
                return f"{SignUp.PACKET_ID.decode()}Client already exists"
            data["users"].update({name.strip(): (password, message)})
            f.seek(0)
            json.dump(data, f, indent=4)

        return f"{SignUp.PACKET_ID.decode()}logged in, nice"

    @staticmethod
    def get_headers(message: bytes):
        """
        gets the headers for the protocol
        :param message: message
        :return: the headers
        """
        name = message[1:33].decode()
        password = message[33:65].decode()
        return name, password


class Login:
    """
    logs in to an existing client
    """
    PACKET_ID = b'\x03'
    SOCKET_TYPE = "TCP"
    DATA_TYPE = str
    HEADER_SIZE = 65

    @staticmethod
    def match(message: bytes, socket_type: str, client_data: Dict[str, any]) -> bool:
        """
        checks
        :param message: the data sent by the socket
        :param socket_type: the type of the socket TCP/UDP
        :param client_data: the data of the specified client
        :return: weather it matches the protocol
        """
        return socket_type == Login.SOCKET_TYPE and message[0] == Login.PACKET_ID[
            0] and "user_name" not in client_data and len(message) >= Login.HEADER_SIZE

    @staticmethod
    def get_answer(headers, _message: Union[str, bytes], client_data: Dict[str, any],
                   clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        Function gets a message which follows the protocol and sends everyone the message of the client.
        as well as a message for the client which sent it that it was received
        :param headers: requested name and password(in md5hash)
        :param _message: no need for data here
        :param client_data: the data of the client
        :param clients: data of the clients
        :return: what to return to the client
        """
        name, password = headers
        name = name.strip()
        with open("users.json", "r") as f:
            data: dict = json.load(f)
        if name not in data["users"] or data["users"][name][0] != password:
            return f"{Login.PACKET_ID.decode()}{False.to_bytes(2, 'big').decode()}" \
                   f"invalid password or user_name".ljust(32)
        url = data["users"][name][1]
        client_data["user_name"] = name
        msg = f"{Login.PACKET_ID.decode()}{client_data['ID'].to_bytes(2, 'big').decode()}" \
              f"{name.ljust(32)}{url}"
        for data in clients:
            if data["ID"] != client_data["ID"] and "user_name" in data:
                data["tcp_message_queue"].put(msg)

        return msg

    @staticmethod
    def get_headers(message: bytes):
        """
        gets the headers for the protocol
        :param message: message
        :return: the headers
        """
        name = message[1:33].decode()
        password = message[33:65].decode()
        return name, password


protocols = [SignUp, Login]
