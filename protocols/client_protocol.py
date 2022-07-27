"""
this
file will have everything we could do with the client
"""
from typing import Any, Dict, List, Protocol, runtime_checkable, Tuple, Union


@runtime_checkable
class ClientCommand(Protocol):
    """
    Protocol of how messages work
    """
    PACKET_ID: bytes
    SOCKET_TYPE: str
    DATA_TYPE: type
    HEADER_SIZE: int

    @staticmethod
    def match(message: bytes, socket_type: str, client_data: Dict[str, any]) -> bool:
        """
        function meant to check if a packet matches the protocol of a command
        :param message: the message to check
        :param socket_type: the type of the socket UDP/TCP
        :param client_data: the data of the specified client that sent it
        """
        ...

    @staticmethod
    def get_answer(headers: Tuple[any], message: Union[str, bytes], client_data: Dict[str, any],
                   clients: List[Dict[str, any]]) -> Union[str, bytes]:
        """
        function meant to read the message and return what to send back to the client
        :param headers: the headers of the packet
        :param message: the message, either an str or bytes
        :param client_data: the client that sent the packet
        :param clients: the clients dictionary
        """
        ...

    @staticmethod
    def get_headers(message: bytes) -> Tuple[Any, ...]:
        """
        Gets the headers of a message
        """
        ...


def register_protocol(protocol: ClientCommand):
    """
    adds a protocol to the list of protocols
    :param protocol: the protocol
    """
    data["protocols"][protocol.__name__] = protocol


def use_protocol(message, socket_type, client_data, clients_data):
    """
    goes through all the protocols and checks if it matches, if it doesn't error protocol
    :param message: the Packet to check
    :param socket_type:
    :param client_data:
    :param clients_data:
    """
    for protocol in data["protocols"].values():
        if not protocol.__name__.startswith("_") and protocol.match(message, socket_type, client_data):
            headers = protocol.get_headers(message)
            message = message[protocol.HEADER_SIZE:]
            if protocol.DATA_TYPE == str:
                message = message.decode()
            return protocol.get_answer(headers, message, client_data, clients_data.values())
    return b"\x00Error protocol not found/invalid"


data = {"protocols": {}}


template_class = ClientCommand
