"""
everything about events
"""

subscribers = dict()


def subscribe(event_type: str, fn):
    """
    adds function to event, if event exists, else creates event and starts it with the shit
    :param event_type: name/id of the event
    :param fn: function to set
    """
    if event_type not in subscribers:
        subscribers[event_type] = [fn]
    else:
        subscribers[event_type].append(fn)


def post_event(event_type, *args, **kwargs):
    """

    :param event_type:
    :param args: any arguments to send to the functions
    :param kwargs: any key word arguments to send to the functions
    """
    if event_type not in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(*args, **kwargs)


__all__ = ["subscribe", "post_event"]
