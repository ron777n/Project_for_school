"""
for every event in the pygame events
"""

import pygame

from Utils.events import post_event, create_event

events = ("click_down", "click_up", "quit", "base_key_down")

for event_ in events:
    create_event(event_)


def check_events(events_list):
    """
    checks every event and posts it if it is useful for us
    """
    for pygame_event in events_list:
        if pygame_event.type == pygame.QUIT:
            post_event("quit")
        elif pygame_event.type == pygame.KEYDOWN or pygame_event.type == pygame.KEYUP:
            post_event("base_key_down", pygame_event.type == pygame.KEYDOWN, pygame_event.key, pygame_event.mod,
                       pygame_event.unicode)
        elif pygame_event.type == pygame.KEYUP:
            post_event("key_up", pygame_event.key)
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            post_event("click_down", pygame_event.pos, pygame_event.button)
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            post_event("click_up", pygame_event.pos, pygame_event.button)
