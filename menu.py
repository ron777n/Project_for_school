"""
this is the menu shit
"""
import pygame

from Utils.events import event, post_event
from Utils.Pygame import Gui

gui_widgets = pygame.sprite.Group()
events = "start_server",


def start_screen(window_size):
    """
    the screen at the start of the game.
    @param window_size: the size of the window, tuple of (x, y)
    """
    gui_widgets.empty()
    widget_data = [[("button", (250, 140), ("Start", "start_game", 60), {"specific_event": True}),
                    ("button", (260, 140), ("Options", "open_options", 60), {})],
                   [("button", (250, 140), ("Login", "login_button", 60),
                     {"specific_event": lambda: login_screen(window_size)})],
                   [("button", 2, ("Exit", "quit", 60), {"specific_event": True})],
                   ]
    buttons = Gui.grid_gui(window_size, widget_data)
    for button in buttons:
        gui_widgets.add(button)


def login_screen(window_size):
    """
    the login screen
    @param window_size: the size of the window, tuple of (x, y)
    """
    gui_widgets.empty()
    name_box = Gui.InputBox((0, 0), (300, 100), (255, 255, 255))
    password_box = Gui.InputBox((0, 0), (300, 100), (255, 255, 255))

    def post_login_attempt(sign_up=False):  # stretching it but fine
        """
        posts the login attempt event
        """
        name, password = name_box.text, password_box.text
        if not name or not password:
            return
        post_event("on_login_attempt" if not sign_up else "on_sign_up_attempt", name, password)

    widget_data = [
        [
            Gui.Label((0, 0), (200, 100), (0, 0, 0), "Name:", text_color=(255, 255, 255)),
            name_box
        ],
        [
            Gui.Label((0, 0), (200, 100), (0, 0, 0), "Password:", text_color=(255, 255, 255)),
            password_box
        ],
        [("button", 2, ("Back", "Back", 60), {"specific_event": lambda: start_screen(window_size)}),
         ("button", 2, ("Login", "on_login", 60), {"specific_event": lambda: post_login_attempt(False)})]
    ]
    widgets = Gui.grid_gui(window_size, widget_data)
    for widget in widgets:
        gui_widgets.add(widget)


@event
def click_down(mouse_pos, click_id):
    """
    checks if clicked a button
    :param mouse_pos: where the mouse is
    :param click_id: what type of click user clicked, eg: right or left mouse button
    """
    if click_id == 1:
        widget: Gui.BaseGui
        for widget in gui_widgets:
            # if widget.rect.collidepoint(mouse_pos):
            widget.click(mouse_pos, True)


@event
def click_up(mouse_pos, click_id):
    """
    checks if clicked a button
    :param mouse_pos: where the mouse is
    :param click_id: what type of click user clicked, eg: right or left mouse button
    """
    if click_id == 1:
        widget: Gui.BaseGui
        for widget in gui_widgets:
            widget.click(mouse_pos, False)
