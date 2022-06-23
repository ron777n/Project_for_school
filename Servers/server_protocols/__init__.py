"""
this
file will have everything we could do with the client
"""
import importlib
from typing import List, Protocol, runtime_checkable, Tuple, Union
from Main_project.Utils.events import *
import os
import logging


@runtime_checkable
class ServerCommand(Protocol):
    """
    Protocol of how messages work
    """
    PACKET_ID: bytes
    SOCKET_TYPE: str
    DATA_TYPE: type
    EVENT_TYPE: str

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


protocols: List[ServerCommand] = []
events = {}


def register_protocol(protocol: ServerCommand):
    """
    adds a protocol to the list of protocols
    :param protocol:
    """
    protocols.append(protocol)
    events[protocol.EVENT_TYPE] = protocol


def call_protocol(message):
    """
    calls the matching protocol's event
    :param message:
    """
    for protocol in protocols:
        if protocol.PACKET_ID[0] == message[0]:
            packet_id, *headers, data = protocol.get_message_data(message)
            post_event(protocol.EVENT_TYPE, data, *headers)
            return
    print("Protocol not supported yet or missed")
    return


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
                    if isinstance(protocol, ServerCommand):
                        register_protocol(protocol)
                        logging.debug(f"Loaded protocol \"{protocol}\" from library {m.__name__}")
                    else:
                        logging.warning(f"Library {m.__name__} protocol: \"{protocol}\" does not follow protocol,"
                                        f" skipping to next one")
            else:
                logging.warning(f"Library: {m.__name__} does not follow protocol, skipping to next one")


__all__ = ["call_protocol", "events"]


load_modules()
