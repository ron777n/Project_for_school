"""
this is for any gui utils i might have
"""
import pygame
from Utils.events import get_subscribers, post_event, create_event, clear_event, unsubscribe

# import textwrap
from Utils.Pygame.texting import *

events = ["button_click"]
for event in events:
    create_event(event)


# def wrap_text(text, width, height, font_name="Comic Sans MS"):
#     font = pygame.font.SysFont(font_name, text_size)


class BaseGui(pygame.sprite.Sprite):
    """
    The basic gui for the screen
    """

    def __init__(self, position, background_image, size=None):
        super().__init__()
        width, height = 0, 0
        if isinstance(background_image, tuple):
            assert isinstance(size, tuple), "you need to specify width and height in size if background is static"
            width, height = size
            background_image_ = pygame.Surface((width, height))
            background_image_.fill(background_image)
            background_image = background_image_
        assert isinstance(background_image, pygame.Surface), "invalid background type"
        if isinstance(size, int):
            width = background_image.get_width() * size
            height = background_image.get_height() * size
        elif isinstance(size, tuple) and (width, height) == (0, 0):
            width, height = size
        else:
            width = background_image.get_width()
            height = background_image.get_height()
        self._image = pygame.transform.scale(background_image, (int(width), int(height)))
        self.rect = self._image.get_rect()
        self.image = self._image.copy()
        self.size = self.image.get_size()
        self.rect.center = position

    def click(self, mouse_pos, click_type):
        """
        when user clicked the screen.
        :param mouse_pos: where the mouse was clicked
        :param click_type: if it's up or down, down-True and up-False
        :return: forgot what i was going with here
        """
        return self.rect.collidepoint(mouse_pos)

    def redraw(self):
        """
        redraws the image
        """
        self.image = self._image.copy()


class Text(pygame.Surface):
    """
    simple text with no background image
    """
    def __init__(self, text: str, color=(0, 0, 0), font=None):
        if font is None:
            font = pygame.font.SysFont('Comic Sans MS', 20)
        elif isinstance(font, int):
            font = pygame.font.SysFont('Comic Sans MS', font)
        assert isinstance(font, pygame.font.Font), "invalid font type"
        self.text = text
        self.color = color
        self.font = font
        size = self.font.size(self.text)
        lines = self.text.count("\n") + 1
        size = size[0], size[1] * lines
        super().__init__(size, pygame.SRCALPHA)
        self.blit(self.font.render(self.text, True, self.color), self.get_rect())

    def draw(self, surface: pygame.Surface):
        """
        draws the text on a surface.
        """
        surface.blit(self, self.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2)))


class InputBox(BaseGui):
    """
    For text input
    """

    def __init__(self, position, size, background_image, font=None, text_color=(0, 0, 0)):
        super().__init__(position, background_image, size)
        self.font = font
        self._text = Text("")
        self.text_color = text_color

    @property
    def text(self):
        """
        gets the actual text of the thing
        :return:
        """
        return self._text.text

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self._text = Text(value, self.text_color, self.font)
        elif isinstance(value, Text):
            self._text = value
            self.text_color = self._text.color
        else:
            raise ValueError("invalid text type")
        self.redraw()
        self._text.draw(self.image)

    def click(self, mouse_pos, click_type):
        """
        checks if button was
        :return:
        """
        action = False

        # check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_pos):
            if click_type:
                start_typing(((pygame.K_RETURN, ("submit",)), (pygame.K_ESCAPE, ("shit",))), self.text, self)
                clear_event("letter_typed", (self.update_text,))
        elif self.update_text in get_subscribers("letter_typed"):
            unsubscribe("letter_typed", self.update_text)
            if get_text_focus() == self:
                pause_typing(True)
        return action

    def update_text(self, _letter, new_text):
        """
        updates the screen with the new shit
        :param _letter: the letter that was changed
        :param new_text: the new version of the text
        """
        self.text = new_text


class Button(BaseGui):
    """
    Button
    """
    def __init__(self, position, image_scale, text, button_name,
                 font=None, specific_event=""):
        super().__init__(position, pygame.image.load("sprites/Gui/Button.png"), image_scale)
        self.text = Text(text, font=font)
        self.button_name = button_name
        self.specific_event = specific_event
        self.clicked = False
        self.text.draw(self.image)

    def click(self, mouse_pos, click_type):
        """
        checks if button was clicked and calls the correct event
        :return: i forgot where i was going with the action ¯|_(ツ)_|¯
        """
        action = False

        # check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_pos):
            if not self.clicked and click_type:
                self.image.set_alpha(255 / 2)
                self.clicked = True
            elif self.clicked and not click_type:
                if not self.specific_event:
                    post_event("button_click", self.button_name + "_button")
                elif callable(self.specific_event):
                    self.specific_event()
                else:
                    post_event(self.button_name)
        if not click_type:
            self.image.set_alpha(255)
            self.clicked = False

        return action


class Label(BaseGui):
    """
    Just a text box
    """
    def __init__(self, position, size, background_image, text, font=None, text_color=(0, 0, 0)):
        super().__init__(position, background_image, size)
        self.font = font
        self._text: Text = Text(text, text_color, font=self.font)
        self._text_color = text_color
        self._update()

    @property
    def text(self):
        """
        gets the actual text
        :return:
        """
        return self._text.text

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self._text = Text(value, self.text_color, self.font)
        elif isinstance(value, Text):
            self._text = value
            self._text_color = self._text.color
        else:
            raise ValueError("invalid text type")
        self._update()

    @property
    def text_color(self):
        """
        gets the text color, for the setter to update the label
        :return:
        """
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value
        self._update()

    def _update(self):
        """
        redraws the text
        """
        self.redraw()
        self._text.draw(self.image)


def grid_gui(window_size, data_):
    """
    creates a screen of widgets by the data in the format:
    data_ =
    row[
        col[
            type, size, (*args), (**kwargs),
            widget
        ]
    ]
    :param window_size: the size of the window, tuple of (x, y)
    :param data_: list of rows which contains the data of each button
    :return: list of widgets
    """
    layout = []
    width, height = window_size
    new_height = height - 200
    rows_count = len(data_) - 1
    for row_index, row in enumerate(data_):
        for col_index, (widget_data) in enumerate(row):
            pos = width // (len(row) + 1) * (col_index + 1), 100 + new_height // rows_count * row_index
            if isinstance(widget_data, BaseGui):
                widget_data.rect.center = pos
                layout.append(widget_data)
                continue
            data_type, size, args, kwargs = widget_data
            if data_type == "button":
                widget = Button(pos, size, *args, **kwargs)
            elif data_type == "input_box":
                widget = InputBox(pos, size, *args, **kwargs)
            else:
                continue
            layout.append(widget)

    return layout
