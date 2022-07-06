"""
this is for any gui utils i might have
"""
import pygame
from Utils.events import post_event, create_event

events = ["button_click"]
for event in events:
    create_event(event)


class Button(pygame.sprite.Sprite):
    """
    Button
    """

    def __init__(self, x, y, text, scale, button_name, text_size=20,
                 specific_event="", image=pygame.image.load("sprites/Gui/Button.png")):
        super().__init__()
        width = image.get_width()
        height = image.get_height()
        self.text = text
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text_ = font.render(text, True, (0, 0, 0))
        text_rect = text_.get_rect(center=(width * scale / 2, height * scale / 2))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.image.blit(text_, text_rect)
        self.button_name = button_name
        self.specific_event = specific_event
        self.clicked = False

    def click(self, click_type):
        """
        checks if button was
        :return:
        """
        action = False

        # check mouseover and clicked conditions
        if not self.clicked and click_type == "DOWN":
            if not self.specific_event:
                post_event("button_click", self.button_name + "_button")
            else:
                post_event(self.button_name)
            self.clicked = True

        if click_type == "UP":
            self.clicked = False

        return action


def button_only_gui(window_size, btn_data):
    """
    creates a screen of only buttons by button_data
    :param window_size: the size of the window, tuple of (x, y)
    :param btn_data: list of rows which contains the data of each button
    """
    buttons = []
    width, height = window_size
    new_height = height - 200
    rows_count = len(btn_data)
    for row_index, row in enumerate(btn_data):
        for col_index, (btn_data_tup, btn_data_dict) in enumerate(row):
            button = Button(width // (len(row) + 1) * (col_index + 1), 100 + new_height // rows_count * row_index,
                            *btn_data_tup, **btn_data_dict)
            buttons.append(button)

    return buttons
