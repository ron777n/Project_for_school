"""
Cancer VideoMessage
"""
import base64

import cv2
import numpy as np


class ImageMessage:
    """
    Protocol of chat command from the server
    """
    PACKET_ID = b'\x05'
    SOCKET_TYPE = "UDP"
    DATA_TYPE = bytes
    EVENT_TYPE = "on_video_sent"

    @staticmethod
    def get_message_data(message: bytes):
        """
        gets the packet_id color and data
        :param message:
        """
        data = base64.b64decode(message)
        np_data = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(np_data, 1)
        return frame,

    @staticmethod
    def format_message(image: np.ndarray):
        """
        formats the message to send to the server
        :param image: message to send
        :return:
        """
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        return f"{ImageMessage.PACKET_ID.decode()}{message}"


protocols = [ImageMessage]
