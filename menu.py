"""
this is the menu shit
"""
import pygame

from Utils.events import event
from Utils.Pygame import Gui

buttons_group = pygame.sprite.Group()
events = "start_server",


def start_screen(window_size):
    """
    the screen at the start of the game.
    @param window_size: the size of the window, tuple of (x, y)
    """
    buttons_group.empty()
    btn_data = [[(("Start", 2, "start_game", 60), {"specific_event": True}),
                 (("Options", 2, "open_options", 60), {})],
                [(("Exit", 2, "quit", 60), {"specific_event": True})]]
    buttons = Gui.button_only_gui(window_size, btn_data)
    for button in buttons:
        buttons_group.add(button)


@event
def click_down(mouse_pos, click_id):
    """
    checks if clicked a button
    :param mouse_pos: where the mouse is
    :param click_id: what type of click user clicked
    """
    if click_id == 1:
        button: Gui.Button
        for button in buttons_group:
            if button.rect.collidepoint(mouse_pos):
                button.click("DOWN")


@event
def click_up(mouse_pos, click_id):
    """
    checks if clicked a button
    :param mouse_pos: where the mouse is
    :param click_id: what type of click user clicked
    """
    if click_id == 1:
        button: Gui.Button
        for button in buttons_group:
            if button.rect.collidepoint(mouse_pos):
                button.click("UP")

