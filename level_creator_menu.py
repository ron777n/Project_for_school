"""
Menu, because menus
"""
import json

import pygame

with open("settings.json") as f:
    settings = json.load(f)


class Menu:
    """
    Menu, because menus
    """
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

    def create_menu(self):
        """
        creates the actual menu of the game
        """
        pass

    def display(self):
        """
        displays the menu on the window.
        """
        pass
