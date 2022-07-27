"""
this
file will have everything we could do with the client
"""
from typing import Protocol, runtime_checkable, Tuple, Union
import logging

LOGGING_LEVEL = logging.WARNING


@runtime_checkable
class ServerCommand(Protocol):
    """
    Protocol of how messages work
    """
    PACKET_ID: bytes
    SOCKET_TYPE: str
    DATA_TYPE: type
    EVENT_TYPE: str
    SENDING_HEADERS: int

    @staticmethod
    def get_message_data(message: bytes) -> Tuple[any, ...]:
        """
        gets the headers of the message
        :param message: message from the server
        """
        ...

    @staticmethod
    def format_message(*args, **kwargs) -> Union[str, bytes]:
        """
        formats the message to send to the server
        :param args: all the arguments to send to the function
        :param kwargs: the the kwargs to send to the function
        :return:
        """
        ...


data = {"protocols": {}, "events": {}}


def register_protocol(protocol: ServerCommand):
    """
    adds a protocol to the list of protocols
    :param protocol:
    """
    data["protocols"][protocol.__name__] = protocol
    data["events"][protocol.EVENT_TYPE] = protocol


logger = logging.getLogger(__name__)

logger.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter("%(created)f: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def use_protocol(message, socket_type):
    """
    calls the matching protocol's event
    :param message: the message from the socket
    :param socket_type: the type of the socket
    """
    for protocol in data["protocols"].values():
        if not protocol.__name__.startswith("_") and protocol.SOCKET_TYPE == socket_type and protocol.PACKET_ID[0] == \
                message[0]:
            return protocol

    logging.debug(f"Protocol not supported yet or missed for {message}")
    return


template_class = ServerCommand
