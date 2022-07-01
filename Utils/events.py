"""
everything about events
"""
from functools import wraps
import logging
logger = logging.getLogger(__name__)

logger.setLevel(logging.WARNING)
formatter = logging.Formatter("%(created)f: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

subscribers = dict()


def subscribe(event_type: str, fn):
    """
    adds function to event, if event exists, else creates event and starts it with the shit
    :param event_type: name/id of the event
    :param fn: function to set
    """
    if event_type not in subscribers:
        logger.warning(f"warning, event {event_type} doesn't seem to exist,"
                       f" will still create new event for you but might not work")
        subscribers[event_type] = [fn]
    else:
        subscribers[event_type].append(fn)


def create_event(event_type):
    """
    creates an event, made so it'd be easier to debug if missed or reused event_types
    :param event_type: name/id of the event
    """
    if event_type in subscribers:
        logger.warning(f"event {event_type} created more than once")
    else:
        subscribers[event_type] = []


def post_event(event_type, *args, **kwargs):
    """
    calls an event
    :param event_type:
    :param args: any arguments to send to the functions
    :param kwargs: any key word arguments to send to the functions
    """
    if event_type not in subscribers:
        logger.warning(f"{event_type} has no subscribers")
        return
    logger.debug(f"{event_type} called with args:{args} and kwargs: "
                 f"{kwargs} to {len(subscribers[event_type])} functions")
    for fn in subscribers[event_type]:
        fn(*args, **kwargs)


def event(event_type):
    """
    registers a function to a server message
    :param event_type: the type of the event
    :return:
    """

    def decorator(fnc):
        """
        to add the event we must create a new function
        :param fnc: the function under the @ sign
        :return: the registered function
        """
        @wraps(fnc)
        def new_function(*args, **kwargs):
            """
            not sure how to explain this but this entire code block just to
            enable @event("en_message") to work
            https://www.youtube.com/watch?v=pr1xfd6oTwY if you want to find out more
            :param args:
            :param kwargs:
            """
            return fnc(*args, **kwargs)
        subscribe(event_, new_function)
        return new_function
    event_ = event_type if not callable(event_type) else "on_echo"
    return decorator


__all__ = ["subscribe", "post_event", "event", "create_event"]
