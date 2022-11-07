"""
helps you create new levels
"""
from typing import Type, Optional

import pygame
import pymunk
import pymunk.pygame_util

import leveler
from Utils.Pygame import Gui
from Utils.Pygame.Events import check_events
from Utils.Pygame.Gui.Base import Clickable
from Utils.events import event
from Utils.timing import tick, dt
from camera import CameraGroup
from physics.objects import Block, Solid
from physics.objects.blocks import SlipperyBlock


class ObjectGui(Gui.Button):
    """
    click this for buttons n shit
    """

    def __init__(self, position, size, object_type: Type[Solid], ):
        img = object_type._image
        self.object_type = object_type
        self._image = img
        super().__init__(position, size, img)

    def click(self, mouse_pos, click_type, click_id):
        was_clicked = self.clicked.setdefault(click_id, 0)
        in_rect = super().click(mouse_pos, click_type, click_id)
        if click_id == 1:
            if not click_type:
                if current_block.image == self.object_type._image:
                    current_block.image = None
                if mouse_pos[0] > self.rect.right and was_clicked:
                    spawn(self.object_type, camera_group.mouse)
            elif in_rect and click_type:
                current_block.image = self.object_type._image


class BlocksMenu(Gui.ScrollableGui):
    @property
    def image(self):
        img = super().image
        if current_block.image is not None and self.rect.colliderect(current_block.rect):
            img.set_alpha(255 // 2)
        return img


class ObjectButton(Clickable):
    """
    left click to move it around
    right click to open settings
    """
    def __init__(self, object_type: Type[Solid], position):
        self.type = object_type
        self.position_size = []
        self.kwargs = object_type.__init__.__kwdefaults__.copy()
        super().__init__(position, (100, 100), object_type._image, (self.open_menu, (3,)))
        self.position_size[:2] = self.rect.topleft, (100, 100)

    def click(self, mouse_pos, click_type, click_id):
        was_clicked = self.clicked.setdefault(click_id, 0)
        in_rect = super().click(mouse_pos, click_type, click_id)
        if click_id == 1:
            if not click_type:
                if current_block.image is self.type._image:
                    current_block.image = None
                if mouse_pos[0] > 200 and was_clicked:
                    self.rect.center = mouse_pos
                    self.position_size[0] = self.rect.topleft
                elif mouse_pos[0] < 200 and was_clicked:
                    delete_block(self)
            elif in_rect and click_type:
                current_block.image = self.type._image
                current_block.rect.size = self.position_size[1]

    def spawn(self, space, camera):
        new_block = self.type(space, pygame.Rect(self.position_size), **self.kwargs)
        camera.add(new_block)

    def open_menu(self):
        if self.kwargs["body_type"] == pymunk.Body.DYNAMIC:
            self.kwargs["body_type"] = pymunk.Body.STATIC
        elif self.kwargs["body_type"] == pymunk.Body.STATIC:
            self.kwargs["body_type"] = pymunk.Body.DYNAMIC
        print(f"{self.kwargs=}")


pygame.init()
back_drop = pygame.image.load("ideas/ui/level_creator.png")
cam_shape = back_drop.get_width(), 600
screen = pygame.display.set_mode((back_drop.get_width(), cam_shape[1]))
clock = pygame.time.Clock()
camera_group = CameraGroup(back_drop, cam_shape)
current_block = pygame.sprite.Sprite()
current_block.image = None
current_block.rect = pygame.rect.Rect(0, 0, 100, 100)
properties_gui_size = (250, cam_shape[1])
options = Gui.ScrollableGui((cam_shape[0]-properties_gui_size[0]/2, cam_shape[1]//2), properties_gui_size, pygame.image.load("sprites/Gui/Button.png"))
camera_group.add(options)
options.active = False

level = leveler.Level(back_drop)
blocks: list[ObjectButton] = []
gui_group = Gui.GuiCollection(active=True)


def delete_block(block):
    blocks.remove(block)
    gui_group.remove(block)
    camera_group.remove(block)
    update_blocks()


def spawn(block: Type[Solid], pos):
    btn = ObjectButton(block, pos)
    blocks.append(btn)
    gui_group.add(btn)
    update_blocks()


def update_blocks():
    """
    deletes a block
    """
    global camera_group, level
    camera_group = CameraGroup(back_drop, cam_shape)
    level = leveler.Level(back_drop)


def save_level(back_ground, spawn_point, *data):
    pass


def generate_main_menu(window_screen: Gui.GuiWindow, window_size):
    blocks_menu = BlocksMenu((100, window_size[1] / 2), (200, window_size[1]), )
    block_button = ObjectGui((0, 0), (100, 100), Block)
    blocks_menu.add(block_button)
    block_button = ObjectGui((0, 0), (100, 100), SlipperyBlock)
    blocks_menu.add(block_button)
    start_button = Gui.Button((0, 0), (0, 0), "Start", specific_event=flip_time_pass)
    blocks_menu.add(start_button)
    sartan = Gui.GuiCollection(blocks_menu)
    sartan.active = True
    window_screen.add_screen("main", sartan)


@event
def mouse_moved(position, moved, buttons, touch):
    current_block.rect.center = position


time_pass = False


def flip_time_pass():
    global time_pass
    time_pass = not time_pass
    update_blocks()
    if time_pass:
        for block in blocks:
            block.spawn(level, camera_group)


def main():
    """
    main function
    """
    display = pygame.display.get_surface()
    window = Gui.GuiWindow()
    generate_main_menu(window, cam_shape)
    window.screen = "main"
    _draw_options = pymunk.pygame_util.DrawOptions(display)

    while True:
        check_events(pygame.event.get())

        screen.fill("#71ddee")
        camera_group.update()
        camera_group.draw()

        # space.debug_draw(_draw_options)
        level.step(dt[0])
        if not time_pass:
            gui_group.draw(display)
        window.draw(display)
        if current_block.image is not None:
            screen.blit(pygame.transform.scale(current_block.image, current_block.rect.size), current_block.rect)
            # pygame.draw.rect(screen, (255, 0, 0), current_block, 10)

        pygame.display.update()

        tick(60)


if __name__ == "__main__":
    main()
