"""
Sisyphus' python template.
EGG
TODO breakable objects
TODO acceleration checks
"""
import pygame
import pymunk
import pymunk.pygame_util
from pygame.math import Vector2

from Utils.timing import tick, dt
from Utils.Pygame.Gui import Text
from physics import moving_objects
from physics import objects


interact_able = [objects.Block, objects.Turret]


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

    player = objects.Turret(space, pygame.rect.Rect(600-50, 400-50, 150, 100))
    camera_group.add(player)
    block_left = objects.Block(space, pygame.rect.Rect(50, 50, 100, 500), True)
    block_right = objects.Block(space, pygame.rect.Rect(1000, 50, 100, 500), True)
    block_top = objects.Block(space, pygame.rect.Rect(50, 0, 1050, 100), True)
    block_bottom = objects.Block(space, pygame.rect.Rect(50, 550, 1050, 100), True)
    egg = objects.Block(space, pygame.rect.Rect(800, 300, 100, 100), False)
    new_egg = objects.Block(space, pygame.rect.Rect(500, 300, 100, 100), False)
    moving_objects.LineWay(new_egg, pygame.rect.Rect((250, 170), (500, 150)), True, 30, gravity=False)

    # stationary_blocks = pygame.sprite.Group(block_left, block_right, block_top, block_bottom)
    camera_group.add(block_left, block_right, block_top, block_bottom)
    camera_group.add(egg, new_egg)

    camera_group.add(player)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEMOTION:
                player.turn_to(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    out = player.rect.center
                    direction = Vector2(event.pos) - out
                    new_laser = objects.Laser(space, out, direction, 100)
                    # new_laser.apply_impulse_at_local_point((100, 100), (0, 0))
                    camera_group.add(new_laser)
                elif event.button == pygame.BUTTON_RIGHT:
                    egg.apply_impulse_at_local_point((1000, -1000), (0, 0))

                    # player.angle_to(Vector2(event.pos))

        screen.fill("#71ddee")

        # pygame.draw.rect(screen, (255, 0, 0), player.rect)

        camera_group.update()
        camera_group.draw(screen)

        # space.debug_draw(draw_options)

        fps = clock.get_fps()
        fps = Text(f"{fps:.2f}FPS", (0, 0, 0))
        fps.draw(screen, ("top_left", 5, 10))

        pygame.display.update()

        tick(60)
        space.step(dt[0])


if __name__ == "__main__":
    main()
