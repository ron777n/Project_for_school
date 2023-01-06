"""
for the basics of gui
"""
import copy
from typing import Union, Callable, Iterable, Tuple

import pygame

from Utils import events
from Utils.Pygame.image_utils import generate_image
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
            self._image = generate_image(background_image, size)
            self.size = self._image.get_size() if size is None else size
        else:
            self.size = size
        self.parents = []
        self.rect = pygame.Rect((0, 0), self.size)
        self.start_image = self._image.copy()
        self.start_position = position
        self.rect.center = position
        self.on_update: dict[Callable[..., any], tuple[tuple, dict]] = {}

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

    def change_rect(self,
                    new_rect: Union[float, tuple[float, float], tuple[float, float, float, float], pygame.rect.Rect]):
        """
        changes the rect of the object
        @param new_rect: if float then it's scale for the rect
        if it is a tuple of 2 floats it is the new size
        if it is a rect like object it will just fit it
        @return:
        """

        pos = self.rect.topleft
        size = self.size
        if isinstance(new_rect, pygame.rect.Rect):
            pos = new_rect.topleft
            size = new_rect.size
        elif isinstance(new_rect, tuple):
            if len(new_rect) == 2:
                size = new_rect
            else:
                pos = new_rect[:2]
                size = new_rect[2:]
        else:
            size = size[0] * new_rect, size[1] * new_rect
        pos = [*pos]
        size = [*size]
        if pos[0] < 0:
            pos[0] = self.rect.left
        if pos[1] < 0:
            pos[1] = self.rect.top
        if size[0] < 0:
            size[0] = self.size[0]
        if size[1] < 0:
            size[1] = self.size[1]
        self.size = size
        self.rect.update(pos, size)
        self.update()
        for parent in self.parents:
            parent.add_to_rect(self.rect)

    def update(self, *args: any, **kwargs: any) -> None:
        for function, (args, kwargs) in self.on_update.items():
            function(*args, **kwargs)

    def redraw(self):
        self._image = self.start_image.copy()

    @property
    def image(self) -> pygame.Surface:
        return pygame.transform.scale(self._image, self.rect.size)

    def __str__(self):
        return f"GuiWidget<{self.__class__.__name__}>" \
               f"{'(' + self.text + ')' if hasattr(self, 'text') and self.text else ''}"


class GuiCollection(pygame.sprite.Group, BaseGui):
    """
    a gui that contains more more gui objects in it
    """
    Scrollable_timer = 700

    def __init__(self, *sprites: BaseGui, active=False):
        self._widgets: list[Union[BaseGui, tuple[BaseGui, any]]] = []
        if not hasattr(self, "rect"):
            self.rect = pygame.rect.Rect(0, 0, 0, 0)
        super().__init__()
        BaseGui.__init__(self, (0, 0), (0, 0))
        self._active = active
        self.add(*sprites)

        events.subscribe("click_down", self.click_down)
        events.subscribe("click_up", self.click_up)
        events.subscribe("on_scroll", self.scroll)
        self.scroll_time = Timer(self.Scrollable_timer, False)

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
        if not self.active:
            return
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
        self._widgets.clear()

    def empty(self):
        del self.widgets

    @property
    def image(self) -> pygame.Surface:
        image = super(GuiCollection, self).image
        for widget in self:
            new_rect = widget.rect.copy()
            new_rect.topleft = (widget.rect.left - self.rect.left, widget.rect.top - self.rect.top)
            print(self.parents, self, new_rect)
            image.blit(widget.image, new_rect)
        return image

    def add_to_rect(self, rect):
        if not self.rect:
            if rect:
                self.rect.update(rect)
            return

        left = min(self.rect.left, rect.left)
        top = min(self.rect.top, rect.top)
        self.rect.update((left, top, max(self.rect.right, rect.right) - left, max(self.rect.bottom, rect.bottom) - top))

    def add(self, *sprites: BaseGui) -> None:
        for widget in sprites:
            self.add_to_rect(widget.rect)
            self._widgets.append(widget)
            events.unsubscribe("on_scroll", widget.scroll)
            events.unsubscribe("click_down", widget.scroll)
            events.unsubscribe("click_up", widget.scroll)
            widget.parents.append(self)
            widget.active = self.active

    def change_rect(self,
                    new_rect: Union[float, tuple[float, float], tuple[float, float, float, float], pygame.rect.Rect]):
        rects = [oof.rect.copy() for oof in self]
        size = [*self.size]
        pos = [*self.rect.topleft]
        super().change_rect(new_rect)
        pos_change = self.rect.left - pos[0], self.rect.top - pos[1]
        if not size[0]:
            size[0] = self.size[0]
        if not size[1]:
            size[1] = self.size[1]
        scale = [1, 1]
        if self.size[0] and size[0]:
            scale[0] = self.size[0] / size[0]
        if self.size[1] and size[1]:
            scale[1] = self.size[1] / size[1]
        for (x, y, w, h), widget in zip(rects, self):
            widget.change_rect((pos_change[0] + x * scale[0], pos_change[1] + y * scale[1], w * scale[0], h * scale[1]))
        for parent in self.parents:
            parent.add_to_rect(self.rect)

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

    def scroll(self, mouse_pos, dy):
        if not self.rect.collidepoint(mouse_pos):
            return False
        if not self.scroll_time.check():
            for widget in self:
                if widget.scroll(mouse_pos, dy):
                    return True
            return False
        self.scroll_time.reset()
        return False

    def remove(self, widget):
        self._widgets.remove(widget)

    def __iter__(self) -> Iterable[BaseGui]:
        self.n = -1
        self.copied_widgets = self._widgets.copy()
        self.max_ = len(self.copied_widgets)
        return self

    def __next__(self) -> BaseGui:
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

    def __getitem__(self, item):
        return self._widgets[item]


class GuiWindow(GuiCollection):
    """
    for everything with the gui windows
    """

    def __init__(self, *sprites):
        super().__init__(*sprites)
        self._screen: GuiCollection = GuiCollection()
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
            # self._screen.empty()
            self._screen.active = False
            self.active = False  # del self.widgets
        elif screen_name in self.screens:
            self.active = True
            self._screen.active = False
            self._screen = self.screens[screen_name]
            self._screen.active = True
            self.widgets = self._screen.widgets
        self.rect.update(self._screen.rect)

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
        if hasattr(self, "active") and not self.active:
            return False
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
        self._image = generate_image(background, size)
        BaseGui.__init__(self, position, size, self._image)
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

    def __init__(self, position, max_size, background=None, *widgets, active=False):
        Scrollable.__init__(self, position, max_size, background=background)
        GuiCollection.__init__(self, active=active)
        self.widgets: list[tuple[BaseGui, int]] = []
        self.add(*widgets)

    def add(self, *widgets: BaseGui):
        for widget in widgets:
            if widget.resize_able:
                if widget.size[0] != self.size[0]:
                    widget.change_rect(self.size[0] / widget.size[0])
                widget.on_update[self.update] = (), {}
            widget.change_rect((self.rect.left, self.current_height, -1, -1))
            GuiCollection.add(self, widget)
            self.current_height += widget.rect.h
            print(self, widget, self.current_height)

    def scroll(self, mouse_pos, dy):
        if not self.rect.collidepoint(mouse_pos):
            return False
        a = GuiCollection.scroll(self, mouse_pos, dy)
        if not a:
            Scrollable.scroll(self, mouse_pos, dy)
            self.update()
            return True
        return False  # self.current_height - self.size[1] > self.offset

    @property
    def image(self):
        if not self.active:
            return pygame.surface.Surface(self.size, pygame.SRCALPHA)
        img = super().image
        # print(self.widgets)
        height = 0
        for widget in self:
            # widget_rect
            widget_rect = pygame.rect.Rect(0, height - self.offset + self.rect.top, *widget.rect.size)
            # widget_rect.top =
            if self.rect.top > widget_rect.bottom:
                continue
            elif self.rect.bottom <= widget_rect.top:
                break
            else:
                img.blit(widget.image, widget_rect)
            height += widget.rect.height
        return img

    def click(self, mouse_pos: tuple, click_type: int, click_id: int):
        self.update()
        for widget in self:
            if widget.rect.top < 0:
                continue
            if self.rect.colliderect(widget.rect):
                widget.click(mouse_pos, click_type, click_id)
            elif self.rect.bottom <= widget.rect.bottom:
                break

    def update(self):
        height = 0
        for widget in self:
            height += widget.rect.height
        self.current_height = height


__all__ = ["GuiWindow", "BaseGui", "ScrollableImage", "ScrollableGui", "GuiCollection"]
