"""
for every event in the pygame events
"""
import pygame

from Utils.events import post_event

events = ["click_down", "click_up", "quit", "key_down"]


def check_events(events_list):
    """
    checks every event and posts it if it is usfull for us
    """
    for pygame_event in events_list:
        if pygame_event.type == pygame.QUIT:
            post_event("quit")
        elif pygame_event.type == pygame.KEYDOWN:
            post_event("key_down", pygame_event.key)
        elif pygame_event.type == pygame.KEYUP:
            post_event("key_up", pygame_event.key)
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            post_event("click_down", pygame_event.pos, pygame_event.button)
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            post_event("click_up", pygame_event.pos, pygame_event.button)