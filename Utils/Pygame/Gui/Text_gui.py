"""
for any basic text gui
"""
import textwrap
from typing import Callable, Union, Optional

import pygame

from Utils.Pygame.Gui.Base import ScrollableImage, BaseGui, Clickable
from Utils.Pygame.texting import start_typing, get_text_focus, pause_typing
from Utils.events import post_event, clear_event, get_subscribers, unsubscribe


class Text(pygame.Surface):
    """
    simple text with no background image
    """

    def __init__(self, text: str, color=(0, 0, 0), font=None):
        font = self.create_font(font)
        self.text = text if isinstance(text, str) else ("" if text is None else str(text))
        self.text_color = color
        self.font = font
        self.lines = self.text.split("\n")
        font_size = self.font.size(max(self.lines, key=lambda x: self.font.size(x)[0]))
        self.size = font_size[0], font_size[1] * len(self.lines)
        super().__init__(self.size, pygame.SRCALPHA)
        # super().__init__(self.size)
        for i, line in enumerate(self.lines):
            rect = self.get_rect()
            rect.top = font_size[1] * i
            self.blit(self.font.render(line, True, self.text_color), rect)

    @staticmethod
    def create_font(font):
        if font is None:
            font = pygame.font.SysFont('Comic Sans MS', 20)
        elif isinstance(font, int):
            font = pygame.font.SysFont('Comic Sans MS', font)
        assert isinstance(font, pygame.font.Font), "invalid font type"
        return font

    def draw(self, surface: pygame.Surface, mode=("center",)):
        """
        draws the text on a surface.
        if mode is "center" then no additional arguments are required
        if "left", "right", "up" or "down"(ima add more later) then a buffer of the corner is required as the second
        tuple element
        """
        if mode[0] == "center":
            surface.blit(self, self.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2)))
        elif mode[0] == "left":
            surface.blit(self, self.get_rect(midleft=(mode[1], surface.get_height() / 2)))
        elif mode[0] == "top_left":
            surface.blit(self, self.get_rect(midleft=(mode[1], mode[2])))

    def wrap(self, size) -> 'Text':
        """
        returns a new text containing the same text and color with different font size(not yet) or new lines
        :param size:
        """
        new_text = ""
        if self.size[0] > size[0]:
            for line in self.lines:
                line_size = self.font.size(line)[0]
                if line_size > size[0]:
                    line = textwrap.fill(line, size[0] // 10)
                new_text += line
        else:
            return self
        return Text(new_text, self.text_color, self.font)


class TextBasedGui(BaseGui):
    """
    if number in size is 0 then it takes the size of the text
    """

    def __init__(self, position, size, background_image, text: Optional = None, mode=("center",), font=None,
                 text_color=(0, 0, 0)):
        self._text = Text(text, text_color, font)
        if not size[0]:
            size = self._text.get_width() + 30, size[1]
            position = position[0] + size[0] // 2, position[1]
        if not size[1]:
            size = size[0], self._text.get_height() + 10
            position = position[0], position[1] + size[1] // 2
        BaseGui.__init__(self, position, size, background_image)

        self.mode = mode
        self._text_color = text_color
        self.font = font
        self._text.draw(self._image)

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
            self._text = Text(value, self._text_color, self.font)
        elif isinstance(value, Text):
            self._text = value
            self._text_color = self._text.text_color
            self.font = self._text.font
        else:
            raise ValueError("invalid text type")
        self.redraw()
        self._text.draw(self._image, self.mode)

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
        self.redraw()
        self._text.draw(self.image, self.mode)


class InputBox(TextBasedGui):
    """
    For text input
    """

    def __init__(self, position, size, background_image, font=None, text_color=(0, 0, 0), mode=("left", 5),
                 on_update=()):
        super().__init__(position, size, background_image, "", mode, font, text_color)
        self.font = font
        self._text = Text("")
        self.text_color = text_color
        self.mode = mode
        self.on_update = {func: (args, kwargs) for func, (args, kwargs) in on_update}

    def add_on_update(self, *functions: Callable[[None], any]):
        """
        add a function to when the text input is changed
        """
        self.on_update |= {func: (args, kwargs) for func, (args, kwargs) in functions}

    def click(self, mouse_pos, click_type, click_id):
        """
        checks if widget was clicked
        :return:
        """

        # check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_pos):
            if click_type:
                start_typing(((pygame.K_RETURN, ("submit",)), (pygame.K_ESCAPE, ("shit",))), self.text, self)
                clear_event("letter_typed", (self.update_text,))
        elif self.update_text in get_subscribers("letter_typed"):
            unsubscribe("letter_typed", self.update_text)
            if get_text_focus() == self:
                pause_typing(True)

    # def change_rect(self, new_rect: Union[float, tuple[float, float],
    #                                       tuple[float, float, float, float],
    #                                       pygame.rect.Rect]):
    #     super().change_rect(new_rect)
    #     print("size: ", self.rect.topleft)

    def update_text(self, _letter, new_text):
        """
        updates the screen with the new shit
        :param _letter: the letter that was changed
        :param new_text: the new version of the text
        """
        self.text = new_text
        for fnc in self.on_update:
            fnc(_letter, new_text)

    # @property
    # def image(self) -> pygame.Surface:
    #     return super().image


class Label(TextBasedGui):
    """
    Just a text box
    """

    def __init__(self, position, size, background_image, text, mode=("center",), font=None, text_color=(0, 0, 0)):
        super().__init__(position, size, background_image, text, mode, font, text_color)
        # self.font = font
        # self._text: Text = Text(text, text_color, font=self.font)
        self._text_color = self.text_color
        self.update_text()

    def update_text(self):
        """
        redraws the text
        """
        self.redraw()
        self._text.draw(self._image)


class Button(TextBasedGui, Clickable):
    """
    Button
    """
    resize_able = True
    back_ground = pygame.image.load("sprites/Gui/Button.png")

    def __init__(self, position, size, image, font=None, specific_event=None):
        if not isinstance(image, pygame.Surface):
            background = self.back_ground
        else:
            background = BaseGui.generate_image(image, size)
        if not isinstance(specific_event, tuple) or (len(specific_event) != 3 or
                                                     (len(specific_event) and callable(specific_event[0]))):
            specific_event = (specific_event, (1,))
        if isinstance(image, str):
            TextBasedGui.__init__(self, position, size, background, image, ('center',), font)
            background = self._image
        else:
            BaseGui.__init__(self, position, size, background)
        Clickable.__init__(self, position, self.size, background, specific_event)
        # self.image = self._image.copy()


class ScrollableText(ScrollableImage):
    """
    joined gui that can be added to and scrollable
    """

    def __init__(self, position, size, default_color=(255, 0, 0), default_font=None, background=None):
        super().__init__(position, size, True, True, background)
        self.default_font = Text.create_font(default_font)
        self.default_color = default_color

    def add(self, *texts: Union[Text, str]):
        """
        adds a text or list of texts to the text box
        :param texts:
        """
        for text in texts:
            if isinstance(text, Text):
                text = text.wrap(self.size)
            else:
                text = Text(text, self.default_color, self.default_font)
            self.add_image(text)


__all__ = ["Button", "ScrollableText", "TextBasedGui", "Text", "InputBox", "Label"]
