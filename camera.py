"""
a moving camera
"""
import pygame

from leveler import build_levels, join_levels


class CameraGroup(pygame.sprite.Group):
    """
    all you want to display in the camera
    """
    zoom_cap = (1, 10)

    def __init__(self, back_ground: pygame.surface.Surface, cam_size=(1200, 1000)):
        super().__init__()
        self.ground_surface = back_ground
        self.og_cam_size = cam_size
        if not pygame.get_init():
            self.initiated = False
            return
        self.initiated = True
        self.display_surface = pygame.display.get_surface()
        self._cam_size = self.og_cam_size
        self.display_size = self.display_surface.get_size()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self._cam_size[0] // 2
        self.half_h = self._cam_size[1] // 2

        # ground
        self.map_size = self.ground_surface.get_size()
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))
        self._image = pygame.Surface(self._cam_size)
        self._image.fill("#71ddee")
        self._zoom: float = 1.0

    @property
    def zoom(self):
        """
        sets the cam_size and clamps it to the zoom_cap
        """
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value > self.zoom_cap[1] or value < self.zoom_cap[0]:
            return
        self.cam_size = (self.og_cam_size[0] / value, self.og_cam_size[1] / value)
        self._zoom = value

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
        self.half_w = self._cam_size[0] / 2
        self.half_h = self._cam_size[1] / 2
        self._image = pygame.Surface(self._cam_size)

    def center_target_camera(self, target: pygame.rect.Rect):
        """
        centers the camera to an object
        """
        self.offset.x = min(target.centerx, self.map_size[0] - self.half_w) - self.half_w
        self.offset.x = max(self.offset.x, 0)
        self.offset.y = min(target.centery, self.map_size[1] - self.half_h) - self.half_h
        self.offset.y = max(self.offset.y, 0)

    def snap(self, target: pygame.Rect):
        """
        snaps the camera to the center of a target, does not keep it snapped
        """
        self.center_target_camera(target)
        # ground

    def update(self):
        """
        egg
        """
        if not self.initiated:
            self.__init__()
            return
        self._image.fill("#71ddee")
        ground_offset = self.ground_rect.topleft - self.offset
        self._image.blit(self.ground_surface, ground_offset)
        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite_: sprite_.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self._image.blit(sprite.image, offset_pos)

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
        camera_group.snap(cam_pos)
        camera_group.draw()

        pygame.display.update()
        clock.tick()


if __name__ == '__main__':
    main()
