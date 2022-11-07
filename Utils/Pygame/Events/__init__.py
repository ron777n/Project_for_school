"""
for every event in the pygame events
"""
import sys

import pygame

from Utils.events import post_event, create_event
from Utils.timing import functioned_timers

events = ("click_down", "click_up", "quit", "base_key_down")

for event_ in events:
    create_event(event_)


def check_events(events_list):
    """
    checks every event and posts it if it is useful for us
    """
    for pygame_event in events_list:
        # print(pygame_event)
        if pygame_event.type == pygame.QUIT:
            post_event("on_quit")
            pygame.quit()
            sys.exit()
        elif pygame_event.type == pygame.KEYDOWN or pygame_event.type == pygame.KEYUP:
            post_event("base_key_down", pygame_event.type == pygame.KEYDOWN, pygame_event.key, pygame_event.mod,
                       pygame_event.unicode)
        elif pygame_event.type == pygame.KEYUP:
            post_event("base_key_up", pygame_event.type == pygame.KEYDOWN, pygame_event.key, pygame_event.mod,
                       pygame_event.unicode)
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            post_event("click_down", pygame_event.pos, pygame_event.button)
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            post_event("click_up", pygame_event.pos, pygame_event.button)
        elif pygame_event.type == pygame.MOUSEMOTION:
            post_event("mouse_moved", pygame_event.pos, pygame_event.rel, pygame_event.buttons, pygame_event.touch)
        elif pygame_event.type == pygame.MOUSEWHEEL:
            post_event("on_scroll", pygame.mouse.get_pos(), pygame_event.y)
        elif pygame_event.type == pygame.TEXTINPUT:
            pass
        elif pygame_event.type == pygame.DROPFILE:
            print("E")
        elif pygame_event.type == pygame.USEREVENT_DROPFILE:
            print("A")
        # elif pygame_event.type == pygame.FILE
        else:
            # print(pygame.event.event_name(pygame_event.type))
            pass

    for timer in functioned_timers:
        timer.check()
