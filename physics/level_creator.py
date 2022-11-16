"""
helps you create new levels
"""
from typing import Type

import pygame
import pymunk
import pymunk.pygame_util

import leveler
from Utils.Pygame import Gui
from Utils.Pygame.Events import check_events
from Utils.Pygame.Gui.Base import Clickable
from Utils.events import event
from Utils.Pygame.image_utils import generate_image
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

    def __init__(self, object_type: Type[Solid], position, name: str):
        self.type = object_type
        self.name = name
        super().__init__(position, (100, 100), object_type._image, (self.open_menu, (3,)))
        self.kwargs: dict[str, any] = {"location": self.rect.topleft,
                                       "size": (100, 100),
                                       "block_data": object_type.__init__.__kwdefaults__.copy()}

    def click(self, mouse_pos, click_type, click_id):
        was_clicked = self.clicked.setdefault(click_id, 0)
        was_set = properties_gui.active is self
        in_rect = super().click(mouse_pos, click_type, click_id)
        if click_id == 1:
            if not click_type:
                if current_block.image is self.type._image:
                    current_block.image = None
                if mouse_pos[0] > 200 and was_clicked:
                    self.rect.center = mouse_pos
                    self.kwargs["location"] = self.rect.topleft
                elif mouse_pos[0] < 200 and was_clicked:
                    delete_block(self)
            elif in_rect and click_type:
                current_block.image = self.type._image
                current_block.rect.size = self.kwargs["size"]
        elif click_id == 3:
            if was_clicked and in_rect and was_set:
                properties_gui.active = None

    def spawn(self, space, camera):
        new_block = self.type(space, pygame.Rect(self.kwargs["location"], self.kwargs["size"]),
                              **self.kwargs["block_data"])
        camera.add(new_block)

    def open_menu(self):
        # properties_gui.widgets
        properties_gui.active = self
        if self.kwargs["block_data"]["body_type"] == pymunk.Body.DYNAMIC:
            self.kwargs["block_data"]["body_type"] = pymunk.Body.STATIC
        elif self.kwargs["block_data"]["body_type"] == pymunk.Body.STATIC:
            self.kwargs["block_data"]["body_type"] = pymunk.Body.DYNAMIC
        # print(f"{self.kwargs=}")

    def __str__(self):
        return f"Block<{self.name}>"


class PropertiesGui(Gui.ScrollableGui):
    """
    this is for the properties gui
    """

    @property
    def active(self):
        return super().active

    @active.setter
    def active(self, value):
        if value is True:
            return
        self.empty()
        self.current_height = 0
        super(PropertiesGui, type(self)).active.fset(self, value)
        if isinstance(value, ObjectButton):
            name = Gui.Label((self.rect.left, 25), (250, 50), (0, 0, 0), Gui.Text(value.name, (255, 0, 0)))
            self.add(name)
            # print("NAME FUCK", name, name.rect)
            settings = break_settings_down(value.kwargs)
            # settings.change_rect((0, 50, -1, -1))
            self.add(settings)
            print("settings_rect:", settings, settings.rect)
            # for i, (settings_group, settings) in enumerate(value.kwargs.items(), start=1):
            #     # print(settings_group, settings)
            #     unwrapped = Gui.Text(settings_group.replace("_", " "), (255, 0, 0), 20)
            #     settings_group_name = Gui.Label((0, 0), (100, 50), (0, 0, 0),
            #                                     unwrapped.wrap((100, 50)))
            #     if isinstance(settings, dict):
            #         print(settings)
            #         setting_name = settings
            #     else:
            #         input_box = Gui.InputBox((0, 0), (150, 50), (255, 255, 255))
            #         joined = Gui.join(settings_group_name, input_box)
            #         joined.change_rect((self.rect.left, i*50, 250, 50))
            #         self.add(joined)
            #         # self.add(settings_group_name, input_box)


def break_settings_down(settings: dict) -> Gui.GuiCollection:
    # print(settings)
    general_gui_group = Gui.ScrollableGui((125, 125), (250, 250), (255, 0, 0))
    # general_gui_group.active = True
    for (settings_group, settings) in settings.items():
        if isinstance(settings, dict):
            pass
            # Gui.ScrollableGui((0, 0), (250, 100))
            # a = break_settings_down(settings)
            # # a.change_rect((0, start_location, 250, a.rect.height))
            # general_gui_group.add(a)
        else:
            # print(settings_group, settings)
            unwrapped = Gui.Text(settings_group.replace("_", " "), (255, 0, 0), 20)
            settings_group_name = Gui.Label((0, 0), (100, 50), (0, 0, 0),
                                            unwrapped.wrap((100, 50)))
            input_box = Gui.InputBox((0, 0), (150, 50), (255, 255, 255))
            joined = Gui.join(settings_group_name, input_box)
            # joined.change_rect((0, 0, -1, -1))
            general_gui_group.add(joined)
    return general_gui_group


pygame.init()
# back_drop = pygame.image.load("ideas/ui/level_creator.png")
cam_shape = 1200, 600
back_drop = generate_image(None, cam_shape)
screen = pygame.display.set_mode((cam_shape[0], cam_shape[1]))
clock = pygame.time.Clock()
camera_group = CameraGroup(back_drop, cam_shape)
current_block = pygame.sprite.Sprite()
current_block.image = None
current_block.rect = pygame.rect.Rect(0, 0, 100, 100)
properties_gui_size = (250, cam_shape[1])

level = leveler.Level(back_drop)
blocks: list[ObjectButton] = []
gui_group = Gui.GuiCollection(active=True)
properties_gui = None


def delete_block(block):
    if block not in blocks:
        return
    blocks.remove(block)

    gui_group.remove(block)
    camera_group.remove(block)
    update_blocks()


def spawn(block: Type[Solid], pos):
    if not blocks:
        name = f"{block.__name__} #1"
    else:
        name = blocks[-1].name
        name = f"{block.__name__} #{str(int(name[name.find('#') + 1:]) + 1)}"
    btn = ObjectButton(block, pos, name=name)
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
    global properties_gui
    blocks_menu = BlocksMenu((100, window_size[1] / 2), (200, window_size[1]), )
    block_button = ObjectGui((0, 0), (100, 100), Block)
    blocks_menu.add(block_button)
    block_button = ObjectGui((0, 0), (100, 100), SlipperyBlock)
    blocks_menu.add(block_button)
    start_button = Gui.Button((0, 0), (0, 0), "Physics Check", specific_event=flip_time_pass)
    blocks_menu.add(start_button)
    properties_gui = PropertiesGui((cam_shape[0] - properties_gui_size[0] / 2, cam_shape[1] // 2), properties_gui_size,
                                   pygame.image.load("sprites/Gui/Button.png"))
    gui_group.add(properties_gui)
    sartan = Gui.GuiCollection(blocks_menu, properties_gui)
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
        window.draw(display)

        # space.debug_draw(_draw_options)
        level.step(dt[0])
        if not time_pass:
            gui_group.draw(display)
        # window.draw(display)
        if current_block.image is not None:
            screen.blit(pygame.transform.scale(current_block.image, current_block.rect.size), current_block.rect)
            # pygame.draw.rect(screen, (255, 0, 0), current_block, 10)

        pygame.display.update()

        tick(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\n\n\n\nhave a good day y'all")
