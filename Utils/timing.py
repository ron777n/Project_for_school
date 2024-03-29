"""
timers, clocks and things
"""
import pygame

from Utils.events import post_event


class Timer:
    """
    makes a timer in milliseconds
    specifics:
    can be anything, can be used on anything but the timeout stays.
    """

    def __init__(self, timeout, start=True):
        self.timeout = timeout
        self._specifics = {}
        if start:
            self._specifics[None] = pygame.time.get_ticks()

    def check(self, specific=None):
        """
        returns true timer hasn't ended
        """
        now = pygame.time.get_ticks()
        return now - self._specifics.get(specific, self.timeout) <= self.timeout

    def reset(self, specific=None):
        """
        resets the timer
        """
        self._specifics[specific] = pygame.time.get_ticks()

    def disable(self, specific=None):
        """
        disables/deactivates a timer
        :param specific:
        """
        if specific in self._specifics:
            del self._specifics[specific]


class FunctionedTimer(Timer):
    """
    FUCKED
    """

    def __init__(self, timeout, function: callable = None, *args, reset=False, **kwargs):
        self._reset = reset
        self.function = function
        self.args = args
        self.kwargs = kwargs
        super().__init__(timeout)
        functioned_timers.append(self)

    def check(self, _=None):
        """
        returns True if timer hasn't ended, and calls its function if it has None as well as reset it
        this is being run in the pygame event loop regardless so you don't have to call this manually unless
        you want to actually check it
        :param _:
        :return:
        """
        checked = super().check()
        if not checked:
            if self.function is not None:
                self.function(*self.args, **self.kwargs)
            if self._reset:
                self.reset()
        return checked


fps_clock = pygame.time.Clock()
dt = [1.0]


def tick(fps):
    """
    use this for the fps, it also sets the delta time so important
    :param fps:
    :return:
    """
    try:
        dt[0] = fps_clock.tick(fps) / 100
    except KeyboardInterrupt:
        post_event("quit")
    return dt[0]


functioned_timers: list[FunctionedTimer] = []
