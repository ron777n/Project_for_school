"""
cancer
"""
import pygame

from Utils.events import event, post_event, subscribe
from Utils.Pygame import Gui
from Utils.Pygame.texting import pause_typing

active_screen = pygame.sprite.Group()


def attempt_login(name, password, login):
    """
    posts a login attempt if name and password aren't empty
    """
    print(f"{name.text=}, {password.text=}")
    if name.text and password.text:
        if login:
            post_event("on_login_attempt", name.text, password.text)


class GuiWindow:
    """
    for everything with the gui windows
    """

    def __init__(self, window_size=(1920, 1080)):
        self.in_menu = False
        self.widgets = {}
        self._screen = pygame.sprite.Group()
        self.screens = self.generate_screens(window_size)
        subscribe("click_down", self.click_down)
        subscribe("click_up", self.click_up)

    @property
    def screen(self):
        """
        copies so that if you .clear the screen it would still be fine
        :return:
        """
        return self._screen.copy()

    @screen.setter
    def screen(self, screen_name):
        """
        sets the screen to another screen by it's name
        :param screen_name: the name of the screen in the dict of screens
        """
        assert screen_name in self.screens, "screen not recognized"
        self.set_screen(screen_name)

    def set_screen(self, screen_name):
        """
        sets the screen to another screen by it's name
        :param screen_name: the name of the screen in the dict of screens
        """
        if self.in_menu and (not screen_name or screen_name is None):
            pause_typing()
            self._screen.empty()
            self.in_menu = False
        elif screen_name in self.screens:
            self.in_menu = True
            self._screen = self.screens[screen_name].copy()

    def generate_screens(self, window_size):
        """
        needed to be run after pygame.init() so made it a func instead
        :return:
        """
        screens = {}
        self.widgets["user_button"] = Gui.Button((0, 0), (0, 0), "not logged in", '', 40,
                                                 (self.set_screen, ("login",), {}))
        single_player = Gui.Button((0, 0), (300, 100), "single player", '', 40, (self.set_screen, (None,), {}))
        self.widgets["multi_player"] = Gui.Button((0, 0), (300, 100), "multi-player", '', 40, (self.set_screen, ("login",), {}))
        leave_button = Gui.Button((0, 0), (0, 100), "leave", '', 40, pygame.event.Event(pygame.QUIT))
        option_button = Gui.Button((0, 0), (200, 100), "options", '', 40)
        main_grid = Gui.grid_layout(window_size, [[single_player], [self.widgets["multi_player"]],
                                                  [leave_button, option_button]])
        screens["main_menu"] = pygame.sprite.Group(*main_grid, self.widgets["user_button"])

        name_label = Gui.Label((0, 35), (0, 70), (0, 0, 0), "Name:", text_color=(255, 255, 255))
        name_box = Gui.InputBox((0, 35), (500, 70), (255, 255, 255))
        name_pack = Gui.join(name_label, name_box, should_copy=False)

        password_label = Gui.Label((0, 35), (0, 70), (0, 0, 0), "Password:", text_color=(255, 255, 255))
        password_box = Gui.InputBox((0, 35), (500, 70), (255, 255, 255))
        password_pack = Gui.join(password_label, password_box, should_copy=False)

        back_button = Gui.Button((0, 0), (0, 100), "Back", '', 40, (self.set_screen, ("main_menu",), {}))
        submit_button = Gui.Button((0, 0), (0, 100), "Submit", '', 40,
                                   (attempt_login, (name_box, password_box, True), {}))

        login_grid = Gui.grid_layout(window_size, [[name_pack], [password_pack], [back_button, submit_button]])
        screens["login"] = pygame.sprite.Group(name_pack, login_grid)

        return screens

    def click_down(self, mouse_pos, click_id):
        """
        checks if clicked a button
        :param mouse_pos: where the mouse is
        :param click_id: what type of click user clicked, eg: right or left mouse button
        """

        if self.in_menu and click_id == 1:
            for button in self._screen:
                button.click(mouse_pos, 1)

    def click_up(self, mouse_pos, click_id):
        """
        checks if clicked a button
        :param mouse_pos: where the mouse is
        :param click_id: what type of click user clicked, eg: right or left mouse button
        """
        if self.in_menu and click_id == 1:
            for button in self._screen:
                button.click(mouse_pos, 0)
