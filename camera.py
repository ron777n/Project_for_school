"""
a moving camera
"""
import pygame

from leveler import build_levels, join_levels


class CameraGroup(pygame.sprite.Group):
    """
    all you want to display in the camera
    """

    def __init__(self, back_ground: pygame.surface.Surface):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.cam_size = self.display_surface.get_size()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        # ground
        self.ground_surface = back_ground
        self.map_size = self.ground_surface.get_size()
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))

    def center_target_camera(self, target: pygame.rect.Rect):
        """
        centers the camera to an object
        """
        self.offset.x = min(target.centerx, self.map_size[0] - self.half_w) - self.half_w
        self.offset.x = max(self.offset.x, 0)
        self.offset.y = min(target.centery, self.map_size[1] - self.half_h) - self.half_h
        self.offset.y = max(self.offset.y, 0)

    def custom_draw(self, snapped):
        """
        draws everything
        """
        self.center_target_camera(snapped)
        # ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surface, ground_offset)

        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite_: sprite_.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class CameraMark(pygame.sprite.Sprite):
    """
    marks where the center of the camera is
    """
    def __init__(self, target: pygame.rect.Rect):
        super().__init__()
        self.image = pygame.surface.Surface((100, 100))
        self.image.fill((255, 0, 0))
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
            elif event.type == pygame.KEYUP:
                pass

        screen.fill("#71ddee")

        camera_group.update()
        camera_group.custom_draw(cam_pos)

        pygame.display.update()
        clock.tick()


if __name__ == '__main__':
    main()
