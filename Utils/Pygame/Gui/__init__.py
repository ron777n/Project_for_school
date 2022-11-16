"""
this is for any gui utils i might have
"""

from Utils.events import create_event
from .Base import BaseGui, GuiWindow, ScrollableGui, ScrollableImage, GuiCollection
from .Text_gui import TextBasedGui, Button, InputBox, Label, Text, ScrollableText

events = ["button_click"]
for event in events:
    create_event(event)


def grid_layout(size, widgets: list[list[BaseGui]]) -> GuiCollection:
    """

    :param size:
    :param widgets:
    """
    widgets_list = GuiCollection()
    row_per = size[1]/(len(widgets)+1)
    for row_index, row in enumerate(widgets, start=1):
        col_per = size[0]/(len(row)+1)
        for col_index, widget in enumerate(row, start=1):
            widget.change_rect((col_index * col_per - widget.rect.size[0]/2,
                                row_index * row_per - widget.rect.size[1]/2, -1, -1))
            widgets_list.add(widget)
    return widgets_list


def join(*sprites, _align="horizontal", should_copy=True) -> GuiCollection:
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
        new_sprites[-1].change_rect((new_sprites[-2].rect.right, new_sprites[-2].rect.top, -1, new_sprites[-2].rect.h))
    return GuiCollection(*new_sprites)


__all__ = ["Label", "InputBox", "ScrollableImage", "Text", "TextBasedGui", "ScrollableText", "Button",
           "ScrollableGui", "BaseGui", "join", "grid_layout", "GuiWindow", "GuiCollection"]
