"""
timers, clocks and things
"""
import pygame


class Timer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.specifics = {None: pygame.time.get_ticks()}

    def check(self, specific=None):
        now = pygame.time.get_ticks()
        return now - self.specifics.get(specific, self.timeout) <= self.timeout

    def reset(self, specific=None):
        self.specifics[specific] = pygame.time.get_ticks()
