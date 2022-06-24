"""
this
file will have everything we could do with the client
"""
from typing import Any, Dict, List, Protocol, runtime_checkable, Tuple, Union
import os
import importlib
import logging


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
    def get_answer(headers: bytes, message: Union[str, bytes], client_data: Dict[str, any],
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


protocols: List[ClientCommand] = []


def register_protocol(protocol: ClientCommand):
    """
    adds a protocol to the list of protocols
    :param protocol:
    """
    protocols.append(protocol)


def use_protocol(message, socket_type, client_data, clients_data):
    """
    goes through all the protocols and checks if it matches, if it doesn't error protocol
    :param message: the Packet to check
    :param socket_type:
    :param client_data:
    :param clients_data:
    """
    for protocol in protocols:
        if protocol.match(message, socket_type, client_data):
            packet_id, *headers = protocol.get_headers(message)
            message = message[protocol.HEADER_SIZE:]
            if protocol.DATA_TYPE == str:
                message = message.decode()
            return protocol.get_answer(headers, message, client_data, clients_data.values())
    return b"\x00Error protocol not found/invalid"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(created)f: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def load_modules():
    """
    loads every file in the directory
    """
    if __name__ == '__main__':
        path = ''
        files = os.listdir()
    else:
        path = __name__+"."
        files = os.listdir(__name__.replace(".", "\\"))
    for file in files:
        if not file.startswith("__"):
            m = importlib.import_module(f"{path}{file[:-3]}")
            if hasattr(m, "protocols") and isinstance(m.protocols, list):
                for protocol in m.protocols:
                    if isinstance(protocol, ClientCommand):
                        register_protocol(protocol)
                        logging.debug(f"Loaded protocol \"{protocol}\" from library {m.__name__}")
                    else:
                        logging.warning(f"Library {m.__name__} protocol: \"{protocol}\" does not follow protocol,"
                                        f" skipping to next one")
            else:
                logging.warning(f"Library: {m.__name__} does not follow protocol, skipping to next one")


load_modules()
