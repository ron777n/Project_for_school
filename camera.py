"""
a moving camera
"""
import pygame

from Utils.Pygame.Gui import BaseGui
from leveler import build_levels, join_levels
from Utils.Pygame.targeting import BoundTracker
from Utils.timing import dt


class CameraGroup(pygame.sprite.Group, BoundTracker):
    """
    all you want to display in the camera
    """
    zoom_cap = (1, 10)
    zoom_time = 10

    def __init__(self, back_ground: pygame.surface.Surface, cam_size=(1200, 1000), *sprites):
        super().__init__(*sprites)
        # real basics
        self._target = None
        if not isinstance(back_ground, pygame.surface.Surface):
            back_ground = BaseGui.generate_image(back_ground, cam_size)
        self.ground_surface = back_ground
        self.og_cam_size = cam_size
        self.map_size = self.ground_surface.get_size()
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))
        BoundTracker.__init__(self, self.ground_surface.get_size(), None, ((0, 0), cam_size))
        if not pygame.get_init():
            self.initiated = False
            return
        self.initiated = True

        # basics
        self.display_surface = pygame.display.get_surface()
        self._cam_size = self.og_cam_size
        self.display_size = self.display_surface.get_size()

        # boy he zooming
        self.last_zoom = pygame.Vector2(1)
        self.dest_zoom = pygame.Vector2(1)
        self.lerp_amount = 0
        self._zoom: float = 1.0

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self._cam_size[0] // 2
        self.half_h = self._cam_size[1] // 2

        # ground
        self._image = pygame.Surface(self._cam_size)
        self._image.fill("#71ddee")

        # mouse
        self.mouse_rect = pygame.Rect((0, 0), (1, 1))

    @property
    def global_mouse(self):
        x, y = self.mouse
        x = self.offset.x + x // self._zoom
        y = self.offset.y + y // self._zoom
        return round(x), round(y)

    @property
    def mouse(self):
        return pygame.mouse.get_pos()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if hasattr(value, "rect"):
            value = value.rect
        self._target = value
        self.snap()

    @target.deleter
    def target(self):
        self._target = None

    @property
    def zoom(self):
        """
        sets the cam_size and clamps it to the zoom_cap
        """
        return self.dest_zoom.x

    @zoom.setter
    def zoom(self, value):
        if value > self.zoom_cap[1] or value < self.zoom_cap[0]:
            return
        self.last_zoom.update(self._zoom)
        self.dest_zoom.update(value)
        self.lerp_amount = 0

    @property
    def cam_size(self):
        """
        egg
        """
        return self.cam_size

    @cam_size.setter
    def cam_size(self, value):
        value = tuple(value)
        assert len(value) == 2, "bro... what kinda size is that?"
        self._cam_size = value
        self.size = value
        self.half_w = self._cam_size[0] / 2
        self.half_h = self._cam_size[1] / 2
        self._image = pygame.Surface(self._cam_size)

    def update(self, *args):
        """
        egg
        """
        if not self.initiated:
            self.__init__(self.ground_surface, self.og_cam_size, self.sprites())
            return
        if self._zoom != self.dest_zoom.x:
            self.lerp_amount = min(self.lerp_amount + dt[0]/self.zoom_time, 1)
            self._zoom = self.last_zoom.lerp(self.dest_zoom, self.lerp_amount).x
            self.cam_size = (self.og_cam_size[0] / self._zoom, self.og_cam_size[1] / self._zoom)
        if self._target is not None:
            self.snap()
        self._image.fill("#71ddee")
        ground_offset = self.ground_rect.topleft - self.offset
        self._image.blit(self.ground_surface, ground_offset)
        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite_: sprite_.rect.centery):
            if not hasattr(sprite, "rect"):
                continue
            offset_pos = sprite.rect.topleft - self.offset
            if hasattr(sprite, "image"):
                self._image.blit(sprite.image, offset_pos)
        self.mouse_rect.center = self.global_mouse
        super().update()

    def draw(self, **kwargs):
        """
        draws everything
        """
        img = pygame.transform.scale(self._image, self.display_size)
        self.display_surface.blit(img, (0, 0))


class CameraMark(pygame.sprite.Sprite):
    """
    marks where the center of the camera is
    """
    def __init__(self, target: pygame.rect.Rect):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("sprites/camera_icon.png"), (100, 100))
        # self.image.fill((255, 0, 0))
        self.rect = target


def main():
    """
    tests the camera
    """
    pygame.init()
    cam_shape = 600, 600
    screen = pygame.display.set_mode(cam_shape)
    clock = pygame.time.Clock()
    levels = build_levels()
    level = join_levels(levels)
    width, height = level.shape
    camera_group = CameraGroup(level.image)
    cam_pos = pygame.rect.Rect(width//2, height-100, 100, 100)
    cam_mark = CameraMark(cam_pos)
    camera_group.add(cam_mark)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cam_pos.y = min(cam_pos.y + 100, height-100)
                elif event.key == pygame.K_UP:
                    cam_pos.y = max(cam_pos.y - 100, 0)
                elif event.key == pygame.K_LEFT:
                    cam_pos.x = max(cam_pos.x - 100, 0)
                elif event.key == pygame.K_RIGHT:
                    cam_pos.x = min(cam_pos.x + 100, width - 100)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    camera_group.zoom *= 1.5
                elif event.key in (pygame.K_MINUS, pygame.K_PLUS):
                    camera_group.zoom /= 1.5

            elif event.type == pygame.KEYUP:
                pass

        screen.fill("#71ddee")

        camera_group.update()
        camera_group.draw()

        pygame.display.update()
        clock.tick()


if __name__ == '__main__':
    main()
