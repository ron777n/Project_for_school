"""
for the basics of gui
"""
import copy
from typing import Union, Callable, Iterable, Tuple

import pygame

from Utils import events
from Utils.Pygame.texting import pause_typing
from Utils.timing import Timer


class BaseGui(pygame.sprite.Sprite):
    """
    The basic gui for the screen
    """
    resize_able = False

    def __init__(self, position, size=None, background_image=None):
        if hasattr(self, "based_gui"):
            return
        super().__init__()
        self.based_gui = True
        if not hasattr(self, "_image"):
            self._image = BaseGui.generate_image(background_image, size)
            self.size = self._image.get_size() if size is None else size
        else:
            self.size = size
        self.start_image = self._image.copy()
        self.rect = pygame.Rect((0, 0), self.size)
        self.start_position = position
        self.rect.center = position
        self.on_update: dict[Callable[..., any], tuple[tuple, dict]] = {}

    @staticmethod
    def generate_image(image, size) -> pygame.surface.Surface:
        width, height = 0, 0
        if isinstance(image, tuple):
            assert isinstance(size, tuple), "you need to specify width and height in size if background is static"
            width, height = size
            image_ = pygame.Surface((width, height))
            image_.fill(image)
            image = image_
        elif image is None and isinstance(size, (tuple, list)):
            image = pygame.Surface(size, pygame.SRCALPHA)
        assert isinstance(image, pygame.Surface), "invalid background type"
        if isinstance(size, int):
            width = image.get_width() * size
            height = image.get_height() * size
        elif isinstance(size, tuple) and (width, height) == (0, 0):
            width, height = size
        else:
            width = image.get_width()
            height = image.get_height()
        return pygame.transform.scale(image, (int(width), int(height)))

    def click(self, mouse_pos: tuple, click_type: int, button_type: int):
        """
        when user clicked the screen.
        @param mouse_pos: where the mouse was clicked
        @param click_type: if it's up or down, down-True and up-False
        @param button_type: which mouse button it is, left click is 1 for example.
        :return: forgot what i was going with here but ok
        """
        return self.rect.collidepoint(mouse_pos)

    def scroll(self, mouse_pos, up):
        """
        when user scrolled in the screen
        :param mouse_pos: where the cursor was when the user scrolled
        :param up: is that a scroll up
        """
        return False

    def copy(self):  # honestly i don't know why pygame sprites don't have these
        """
        returns a copy of the sprite for reference things
        """
        return copy.copy(self)

    def resize(self, new_size: Union[float, tuple[float, float]]):
        if isinstance(new_size, tuple):
            width, height = new_size
        else:
            width, height = self.size[0] * new_size, self.size[1] * new_size
        self.size = width, height
        self.rect.update(self.rect.topleft, (width, height))
        self.update()

    def update(self, *args: any, **kwargs: any) -> None:
        for function, (args, kwargs) in self.on_update.items():
            function(*args, **kwargs)

    def redraw(self):
        self._image = self.start_image.copy()

    @property
    def image(self) -> pygame.Surface:
        return pygame.transform.scale(self._image, self.rect.size)


class GuiCollection(pygame.sprite.Group, BaseGui):
    """
    a gui that contains more more gui objects in it
    """
    def __init__(self, *sprites: BaseGui, active=False):
        self._widgets: list[Union[BaseGui, tuple[BaseGui, any]]] = []
        super().__init__(*sprites)
        BaseGui.__init__(self, (0, 0), pygame.display.get_window_size())
        self._active = active

        events.subscribe("click_down", self.click_down)
        events.subscribe("click_up", self.click_up)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        for widget in self._widgets:
            if hasattr(widget, "active"):
                widget.active = value

    def draw(self, surface):
        for widget in self:
            surface.blit(widget.image, widget.rect)

    @property
    def widgets(self):
        return self._widgets

    @widgets.setter
    def widgets(self, value):
        self._widgets = value

    @widgets.deleter
    def widgets(self):
        self._widgets = []

    def add(self, *sprites: BaseGui) -> None:
        self._widgets.extend(sprites)

    def click_down(self, mouse_pos, click_id):
        """
        checks if clicked a button
        :param mouse_pos: where the mouse is
        :param click_id: what type of click user clicked, eg: right or left mouse button
        """
        button: BaseGui
        if self.active:
            for button in self:
                button.click(mouse_pos, 1, click_id)

    def click_up(self, mouse_pos, click_id):
        """
        checks if clicked a button
        :param mouse_pos: where the mouse is
        :param click_id: what type of click user clicked, eg: right or left mouse button
        """
        button: BaseGui
        if self.active:
            for button in self:
                button.click(mouse_pos, 0, click_id)

    def __iter__(self):
        self.n = -1
        self.copied_widgets = self._widgets.copy()
        self.max_ = len(self.copied_widgets)
        return self

    def __next__(self):
        self.n += 1
        if self.n < self.max_:
            widget = self.copied_widgets[self.n]
            if isinstance(widget, BaseGui):
                return widget
            return widget[0]
        else:
            raise StopIteration

    def __len__(self):
        return len(self._widgets)

    # def __repr__(self):
    #     return f"<{self.__class__.__name__}({len(self)} sprites)>"


class GuiWindow(GuiCollection):
    """
    for everything with the gui windows
    """

    def __init__(self, *sprites):
        super().__init__(*sprites)
        self._screen = GuiCollection
        # self.screens = self.generate_screens(self.display.get_size())
        self.screens: dict[str: pygame.sprite.Group] = dict()

    @property
    def screen(self):
        """
        copies so that if you .clear the screen it would still be fine
        :return:
        """
        return self._screen

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
        if self.active and (not screen_name or screen_name is None):
            pause_typing()
            self._screen.empty()
            self.active = False
            del self.widgets
        elif screen_name in self.screens:
            self.active = True
            if hasattr(self._screen, "active"):
                self.active = False
            self._screen = self.screens[screen_name]
            if hasattr(self._screen, "active"):
                self.active = True
            self.widgets = self._screen.widgets

    def add_screen(self, name: str, screen: Union[pygame.sprite.Group, GuiCollection]):
        self.screens[name] = screen

    @property
    def image(self):
        if not self.active:
            return pygame.surface.Surface(self.size, pygame.SRCALPHA)
        return super().image


class Clickable(BaseGui):
    def __init__(self, position, size, background, *on_clicks: tuple[any, Iterable[int]]):
        self.clicked = dict()
        self.on_click = {None: []}
        for on_click, click_ids in on_clicks:
            if isinstance(on_click, (pygame.event.EventType, str)):
                # if isinstance(on_click, pygame.event.EventType):
                #     on_click = pygame.event.Event(pygame.QUIT)
                event = on_click
                on_click = lambda: events.post_event(event)
            elif isinstance(on_click, tuple) and len(on_click) == 3:
                fnc, args, kwargs = on_click
                on_click = lambda: fnc(*args, **kwargs)
            elif on_click is None:
                continue
            elif not callable(on_click):
                raise TypeError("Button class says: FUCK YOU WHAT IS THAT FUNCTION?!?")
            if not click_ids:
                self.on_click[None].append(on_click)
            else:
                for click_id in click_ids:
                    self.on_click[click_id] = on_click
        super().__init__(position, size, background)

    def click(self, mouse_pos, click_type, click_id):
        """
        checks if button was clicked and calls the correct event
        :return: i forgot where i was going with the action ¯|_(ツ)_|¯
        """
        was_clicked = self.clicked.setdefault(click_id, 0)
        # check mouseover and clicked conditions
        if self.rect.collidepoint(*mouse_pos):
            self.clicked[click_id] = 1 if click_type else 0
            if self.clicked[click_id]:
                if click_id == 1:
                    self._image.set_alpha(255 // 2)
            elif was_clicked and not click_type:
                if (func := self.on_click.get(click_id)) is not None:
                    func()

        if not click_type:
            if click_id == 1:
                self._image.set_alpha(255)
            self.clicked[click_id] = 0

        return self.rect.collidepoint(mouse_pos)


class Scrollable(BaseGui):
    """
    it is something you can scroll through
    """

    def __init__(self, position, size, reverse=False, upwards=False, background=None):
        self._offset = 0
        self.reverse = reverse
        self.upwards = upwards
        self.current_height = 0
        self.rect = pygame.Rect(position, size)
        self._image = BaseGui.generate_image(background, size)
        BaseGui.__init__(self, position, size, background)
        self.background = self._image.copy()
        events.subscribe("on_scroll", self.scroll)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        if self.current_height < self.size[1]:
            self._offset = max(self._offset, self.current_height - self.size[1])
            self._offset = min(self._offset, 0)
        else:
            self._offset = max(self._offset, 0)
            self._offset = min(self.current_height - self.size[1], self._offset)

    @property
    def image(self) -> pygame.Surface:
        img = pygame.surface.Surface(self.size, pygame.SRCALPHA)
        img.blit(self.background, (0, 0))
        img.blit(self._image, (0, -self._offset))
        return img

    def scroll(self, mouse_pos, dy):
        if self.rect.collidepoint(mouse_pos):
            self.offset += dy * 10
            return True
        return False


class ScrollableImage(Scrollable):
    """
    it is an image, that you can SCROLL
    """

    def add_image(self, image, scale=False):
        width, height = image.get_size()
        if scale and width != self.size[0]:
            diff = self.size[0] / width
            width *= diff
            height *= diff
            image = pygame.transform.scale(image, (width, height))
        self.current_height += height
        img = self._image.copy()
        self._image = pygame.surface.Surface((self.size[0], self.current_height), pygame.SRCALPHA)
        if self.reverse:
            self._image.blit(img, (0, 0))
            self._image.blit(image, (0, self.current_height - height))
        else:
            self._image.blit(img, (0, height))
            self._image.blit(image, (0, 0))
        self.offset = 0 if not self.upwards else self.current_height - self.size[1]


class ScrollableGui(Scrollable, GuiCollection):
    """
    Gui that you could scroll through
    """
    Scrollable_timer = 700

    def __init__(self, position, max_size, background=None, *widgets):
        Scrollable.__init__(self, position, max_size, background=background)
        GuiCollection.__init__(self)
        self.widgets: list[tuple[BaseGui, int]] = []
        self.add(*widgets)
        self.scroll_time = Timer(self.Scrollable_timer, False)

    def add(self, *widgets: BaseGui):
        for widget in widgets:
            if widget.resize_able:
                if widget.size[0] != self.size[0]:
                    widget.resize(self.size[0] / widget.size[0])
                widget.on_update[self.update] = (), {}
            widget.rect.topleft = self.rect.left, self.current_height
            self._widgets.append((widget, 0))
            events.unsubscribe("on_scroll", widget.scroll)
        self.update()

    def scroll(self, mouse_pos, dy):
        if not self.rect.collidepoint(mouse_pos):
            return False
        if not self.scroll_time.check():
            for widget in self._widgets:
                if widget.scroll(mouse_pos, dy):
                    return True

        super().scroll(mouse_pos, dy)
        self.scroll_time.reset()
        self.update()
        return self.current_height - self.size[1] > self.offset

    @property
    def image(self):
        if not self.active:
            return pygame.surface.Surface(self.size, pygame.SRCALPHA)
        img = super().image
        s_rect = pygame.Rect((0, 0), self.size)
        for widget, height in self.widgets:
            widget_rect = pygame.Rect((0, height - self.offset), widget.size)
            if s_rect.colliderect(widget_rect):
                img.blit(widget.image, widget_rect)
            elif self.rect.bottom <= widget_rect.top:
                break
            # height += widget.rect.size[1]
        return img

    def click(self, mouse_pos: tuple, click_type: int, click_id: int):
        self.update()
        for widget, height in self._widgets:
            if widget.rect.top < 0:
                continue
            if self.rect.colliderect(widget.rect):
                widget.click(mouse_pos, click_type, click_id)
            elif self.rect.bottom <= widget.rect.bottom:
                break

    def update(self):
        height = 0
        for i, (widget, _button) in enumerate(self.widgets):
            widget.rect.top = height - self.offset + self.rect.top
            self.widgets[i] = (widget, height)
            # if hasattr(widget, "text") and "fuck" in widget.text:
            #     print(widget.text, widget.rect)
            height += widget.rect.size[1]
        self.current_height = height
        Scrollable.update(self)


class JoinedGui(GuiCollection):
    """
    groups multiple BaseGui to one
    """

    def __init__(self, *sprites, _pos="center", should_copy=True):
        super().__init__(active=True)
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
            # if hasattr(sprite, "add_on_update"):
            #     sprite.add_on_update(self.update)
            # print(sprite)
            self.add(sprite)
        pos = (min_pos[0] + max_pos[0]) // 2, (min_pos[1] + max_pos[1]) // 2
        size = max_pos[0] - min_pos[0], max_pos[1] - min_pos[1]
        self.rect = pygame.Rect(pos, size)

    def click(self, click_pos, click_type, click_id):
        """
        checks for everything's clicks inside when clicked
        """
        click_pos = click_pos[0] - self.rect[0], click_pos[1] - self.rect[1]
        for sprite in self.sprites:
            sprite.click(click_pos, click_type, click_id)

    @property
    def image(self):
        img = pygame.surface.Surface(self.rect.size, pygame.SRCALPHA)
        img.blits([(sprite.image, sprite.rect) for sprite in self._widgets])
        return img


__all__ = ["GuiWindow", "JoinedGui", "BaseGui", "ScrollableImage", "ScrollableGui", "GuiCollection"]
