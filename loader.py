"""
this
file will have everything we could do with the client
"""
import importlib
import os
import logging
import pathlib
from typing import Union

LOGGING_LEVEL = logging.WARNING

logger = logging.getLogger(__name__)

logger.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter("%(created)f: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


class Load:
    """
    lets you add a protocol library
    put in the name of the template file and the path to the folder with files
    """

    def __init__(self, protocol_template: Union[str, pathlib.Path], protocols_folder: Union[str, pathlib.Path]):
        m = importlib.import_module(protocol_template.replace('/', '.').replace("\\", '.'))
        # print(hasattr(m, "data"), hasattr(m, "register_protocol"),
        #       hasattr(m, "template_class"), hasattr(m, "use_protocol"))
        if hasattr(m, "data") and hasattr(m, "register_protocol") and \
                hasattr(m, "template_class") and hasattr(m, "use_protocol"):
            self.template_class = m.template_class
            self.register_protocol = m.register_protocol
            self.data_start = m.data.copy()
            self.data = m.data
            self.folder_path = protocols_folder
            self.files = os.listdir(protocols_folder)
            self.use_protocol = m.use_protocol
        else:
            raise ValueError(
                "protocol template didn't have the right parameters")  # would've did an if
            # not but pycharm would yell at me for every m. after  # main_class

    def load_modules(self):
        """
        loads every file in the directory
        """
        self.data.clear()
        self.data.update(self.data_start)
        for file in self.files:
            if not file.startswith("_") and file.endswith(".py"):
                m = importlib.import_module(f"{self.folder_path.replace('/', '.').replace(chr(92), '.')}.{file[:-3]}")
                if hasattr(m, "protocols") and isinstance(m.protocols, list):
                    for protocol in m.protocols:
                        if isinstance(protocol, self.template_class):
                            self.register_protocol(protocol)
                            logger.debug(f"Loaded protocol \"{protocol}\" from library {m.__name__}")
                        else:
                            logger.warning(f"Library {m.__name__} protocol: \"{protocol}\" does not follow protocol,"
                                           f" skipping to next one")
                else:
                    print("OOF")
                    logger.warning(f"Library: {m.__name__} does not follow protocol, skipping to next one")
