"""
timers, clocks and things
"""
import pygame


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
        returns true if timer was reset for the specific event before the timeout given
        """
        now = pygame.time.get_ticks()
        return now - self._specifics.get(specific, self.timeout) <= self.timeout

    def reset(self, specific=None):
        """
        resets the timer
        """
        self._specifics[specific] = pygame.time.get_ticks()

    def disable(self, specific=None):
        if specific in self._specifics:
            del self._specifics[specific]


class FunctionedTimer(Timer):
    def __init__(self, timeout, function: callable = None, *args, reset=False, **kwargs):
        self._reset = reset
        self.function = function
        self.args = args
        self.kwargs = kwargs
        super().__init__(timeout)
        functioned_timers.append(self)

    def check(self, _=None):
        checked = super().check()
        if not checked:
            if self.function is not None:
                self.function(*self.args, **self.kwargs)
            if self._reset:
                self.reset()
        return checked


functioned_timers: list[FunctionedTimer] = []
