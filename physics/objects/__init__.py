"""
For the objects
"""

import pygame
import pymunk
import pymunk.pygame_util

from Utils.Pygame.Gui import Text
from Utils.timing import dt, tick

from .basics import BaseObject, Solid
from .blocks import Block, Turret, Laser


def main():
    """
    main function
    """
    pygame.init()
    cam_shape = 1200, 800
    screen = pygame.display.set_mode(cam_shape)
    clock = pygame.time.Clock()
    camera_group = pygame.sprite.Group()

    space = pymunk.Space()
    space.gravity = (0, 10)

    floor = Block(space, pygame.rect.Rect(25, 600, 1000, 100), pymunk.Body.STATIC)
    camera_group.add(floor)

    block1 = Block(space, pygame.rect.Rect(25, 400, 100, 100))
    block1.apply_impulse_at_local_point((1500, -1500), (0, 0))
    # block1.rotate(45)

    camera_group.add(block1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill("#71ddee")

        camera_group.update()
        camera_group.draw(screen)

        fps = clock.get_fps()
        fps = Text(f"{fps:.2f}FPS", (0, 0, 0))
        fps.draw(screen, ("top_left", 5, 10))

        # space.debug_draw(draw_options)

        pygame.display.update()

        tick(60)
        space.step(dt[0])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
