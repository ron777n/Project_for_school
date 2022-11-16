"""
cancer
"""
import pygame

from Utils.Pygame import Gui
from Utils.events import post_event

active_screen = pygame.sprite.Group()


def attempt_login(name, password, login):
    """
    posts a login attempt if name and password aren't empty
    """
    print(f"{name.text=}, {password.text=}")
    if name.text and password.text:
        if login:
            post_event("on_login_attempt", name.text, password.text)


def generate_main_menu(window_screen: Gui.GuiWindow, window_size):
    """
    needed to be run after pygame.init() so made it a func instead
    :return:
    """
    def d_text(value):
        """
        takes a string and transforms it into the default text for the menus
        """
        return Gui.Text(value, (0, 0, 0), 40)
    user_button = Gui.Button((0, 0), (0, 0), d_text("not logged in"), (window_screen.set_screen, ("login",), {}))
    single_player = Gui.Button((0, 0), (300, 100), d_text("single player"), (window_screen.set_screen, (None,), {}))
    multi_player = Gui.Button((0, 0), (300, 100), d_text("multi-player"),
                              (window_screen.set_screen, ("login",), {}))
    leave_button = Gui.Button((0, 0), (0, 100), d_text("leave"), specific_event=pygame.event.Event(pygame.QUIT))
    option_button = Gui.Button((0, 0), (200, 100), d_text("Options"))
    main_grid = Gui.grid_layout(window_size, [[single_player], [multi_player],
                                              [leave_button, option_button]])
    print(main_grid, main_grid.rect)
    window_screen.add_screen("main_menu", Gui.GuiCollection(*main_grid, user_button))

    name_label = Gui.Label((0, 35), (0, 70), (0, 0, 0), Gui.Text("Name:", (255, 0, 0)))
    name_box = Gui.InputBox((0, 35), (500, 70), (255, 255, 255))
    name_pack = Gui.join(name_label, name_box, should_copy=False)

    password_label = Gui.Label((0, 35), (0, 70), (0, 0, 0), Gui.Text("Password:", (255, 0, 0)))
    password_box = Gui.InputBox((0, 35), (500, 70), (255, 255, 255))
    password_pack = Gui.join(password_label, password_box, should_copy=False)

    back_button = Gui.Button((0, 0), (0, 100), d_text("Back"), (window_screen.set_screen, ("main_menu",), {}))
    submit_button = Gui.Button((0, 0), (0, 100), d_text("Submit"),
                               (attempt_login, (name_box, password_box, True), {}))

    login_grid = Gui.grid_layout(window_size, [[name_pack], [password_pack], [back_button, submit_button]])
    window_screen.add_screen("login", login_grid)
