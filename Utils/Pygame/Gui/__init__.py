"""
this is for any gui utils i might have
"""
import textwrap

import pygame
from Utils.events import get_subscribers, post_event, create_event, clear_event, unsubscribe
import copy

from Utils.Pygame.texting import *

events = ["button_click"]
for event in events:
    create_event(event)


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
        self.text_color = color
        self.font = font
        self.lines = self.text.split("\n")
        font_size = self.font.size(max(self.lines, key=lambda x: self.font.size(x)[0]))
        self.size = font_size[0], font_size[1] * len(self.lines)
        super().__init__(self.size, pygame.SRCALPHA)
        for i, line in enumerate(self.lines):
            rect = self.get_rect()
            rect.top = font_size[1] * i
            self.blit(self.font.render(line, True, self.text_color), rect)

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

    def wrap(self, size):
        """
        returns a new text containing the same text and color with different font size(not yet) or new lines
        :param size:
        """
        new_text = ""
        if self.size[0] > size[0]:
            for line in self.lines:
                line_size = self.font.size(line)[0]
                if line_size > size[0]:
                    line = textwrap.fill(line, size[0]//10)
                new_text += line
        else:
            return self
        return Text(new_text, self.text_color, self.font)


class BaseGui(pygame.sprite.Sprite):
    """
    The basic gui for the screen
    """

    def __init__(self, position, size=None, background_image=None):
        super().__init__()
        width, height = 0, 0
        if isinstance(background_image, tuple):
            assert isinstance(size, tuple), "you need to specify width and height in size if background is static"
            width, height = size
            background_image_ = pygame.Surface((width, height))
            background_image_.fill(background_image)
            background_image = background_image_
        elif background_image is None and isinstance(size, (tuple, list)):
            background_image = pygame.Surface(size, pygame.SRCALPHA)
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

    def click(self, mouse_pos: tuple, click_type: int):
        """
        when user clicked the screen.
        :param mouse_pos: where the mouse was clicked
        :param click_type: if it's up or down, down-True and up-False
        :return: forgot what i was going with here but ok
        """
        return self.rect.collidepoint(mouse_pos)

    def redraw(self):
        """
        redraws the image
        """
        self.image = self._image.copy()

    def copy(self):  # honestly i don't know why pygame sprites don't have these
        """
        returns a copy of the sprite for reference things
        """
        return copy.copy(self)


class JoinedGui(BaseGui):
    """
    groups multiple BaseGui to one
    """
    def __init__(self, *sprites, _pos="center", should_copy=True):
        self.sprites: list[BaseGui] = []
        min_pos = [None, None]
        max_pos = [None, None]
        self.copy = should_copy
        for sprite in sprites:
            if should_copy:
                sprite = sprite.copy()
            if min_pos[0] is None or sprite.rect.left < min_pos[0]:
                min_pos[0] = sprite.rect.left
            if min_pos[1] is None or sprite.rect.top < min_pos[1]:
                min_pos[1] = sprite.rect.top
            if max_pos[0] is None or sprite.rect.right > max_pos[0]:
                max_pos[0] = sprite.rect.right
            if max_pos[1] is None or sprite.rect.bottom > max_pos[1]:
                max_pos[1] = sprite.rect.bottom
            if isinstance(sprite, InputBox):
                sprite.on_update.append(self.update)
            self.sprites.append(sprite)
        pos = (min_pos[0] + max_pos[0]) // 2, (min_pos[1] + max_pos[1]) // 2
        size = max_pos[0] - min_pos[0], max_pos[1] - min_pos[1]
        super().__init__(pos, size, (255, 255, 255))
        self.update()

    def click(self, click_pos, click_type):
        """
        checks for everything's clicks inside when clicked
        """
        click_pos = click_pos[0] - self.rect[0], click_pos[1] - self.rect[1]
        for sprite in self.sprites:
            sprite.click(click_pos, click_type)

    def update(self, *args):
        """
        updates everything and redraws them
        """
        self.image.blits([(sprite.image, sprite.rect) for sprite in self.sprites])


class TextBasedGui(BaseGui):
    """
    if number in size is 0 then it takes the size of the text
    """
    def __init__(self, position, size, background_image, text=None, mode=("center",), font=None, text_color=(0, 0, 0)):
        self._text = Text(text, text_color, font)
        if not size[0]:
            size = self._text.get_width() + 30, size[1]
            position = position[0] + size[0] // 2, position[1]
        if not size[1]:
            size = size[0], self._text.get_height() + 10
            position = position[0], position[1] + size[1] // 2
        super().__init__(position, size, background_image)
        self.mode = mode
        self._text_color = text_color
        self.font = font

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
        self._text.draw(self.image, self.mode)

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
        self.on_update = list(on_update)

    def click(self, mouse_pos, click_type):
        """
        checks if widget was clicked
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
        for fnc in self.on_update:
            fnc(_letter, new_text)


class Button(TextBasedGui):
    """
    Button
    """

    def __init__(self, position, size, text, button_name="", font=None, specific_event="", text_mode=("center",)):
        super().__init__(position, size, pygame.image.load("sprites/Gui/Button.png"), text, text_mode, font)
        self.button_name = button_name
        self.specific_event = specific_event
        self.clicked = False
        self._text.draw(self.image)

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
                if isinstance(self.specific_event, (pygame.event.EventType, str)):
                    post_event(self.specific_event)
                elif callable(self.specific_event):
                    self.specific_event()
                elif isinstance(self.specific_event, tuple):
                    fnc, args, kwargs = self.specific_event
                    fnc(*args, **kwargs)
                else:
                    post_event("button_click", self.button_name + "_button")

        if not click_type:
            self.image.set_alpha(255)
            self.clicked = False

        return action


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
        self._text.draw(self.image)


class ScrollableText(BaseGui):
    """
    joined gui that can be added to and scrollable
    """
    def __init__(self, position, size):
        super().__init__(position, size)

    def add(self, *texts):
        """
        adds a text or list of texts to the text box
        :param texts:
        """
        text: Text
        for text in texts:
            text = text.wrap(self.size)
            # self.image.subsurface()
            # self.image = self.image.scroll(0, -text.get_height())
            self.image.blit(text, (0, self.size[1]-text.get_height()))


def grid_layout(size, widgets: list[list[BaseGui]]):
    """

    :param size:
    :param widgets:
    """
    widgets_list: list[BaseGui] = []
    row_per = size[1]/(len(widgets)+1)
    for row_index, row in enumerate(widgets, start=1):
        col_per = size[0]/(len(row)+1)
        for col_index, widget in enumerate(row, start=1):
            widget.rect.centerx = col_index * col_per
            widget.rect.centery = row_index * row_per
            widgets_list.append(widget)
    return widgets_list


def join(*sprites, _align="horizontal", should_copy=True):
    """
    joins a couple of widgets to one active group and returns the active group
    """
    if should_copy:
        new_sprites = [sprites[0].copy()]
    else:
        new_sprites = [sprites[0]]
    for sprite in sprites[1:]:
        if should_copy:
            new_sprites.append(sprite.copy())
        else:
            new_sprites.append(sprite)
        new_sprites[-1].rect.left = new_sprites[-2].rect.right
    return JoinedGui(*new_sprites, should_copy=should_copy)
