"""
enables you to status bro
"""
from pypresence import Presence
from pypresence.exceptions import DiscordNotFound
from threading import Thread
import asyncio
import time


try:
    RTC = Presence(954772507494326363, loop=asyncio.new_event_loop())
except DiscordNotFound:
    RTC = None

started = round(time.time())


def _connect():
    global RTC
    if RTC is None:
        return
    try:
        RTC.connect()
        return
    except RuntimeError:
        pass
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        RTC.connect()
    except RuntimeError:
        RTC = None
        return


if RTC is not None:
    connection_thread = Thread(target=_connect, daemon=True)
    connection_thread.start()


def status(single: bool, floor, ):
    """
    sets the status for the player
    :param single: if he is playing single player
    :param floor: the floor/distance he passed by now
    :return:
    """
    if RTC is None or connection_thread.is_alive():
        return
    RTC.update(state="playing single player" if single else "playing multi-player, somehow?",
               details=f"floor: {floor}" if not isinstance(floor, float) or round(floor) != 43 else "last_floor",
               start=started,
               large_image="sisyphus_game",
               buttons=[{"label": "want to play too?", "url": "https://github.com/ron777n/Project_for_school"}])


def main():
    """
    main function
    """
    status(True, -1)
    while 1:
        pass


if __name__ == "__main__":
    main()
