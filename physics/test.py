"""
Sisyphus' python template.
EGG
"""
from typing import Optional

import pygame
import pymunk
import pymunk.pygame_util
import math

from pygame.math import Vector2

delta_time = 1


def create_ball(space, pos, radius, mass, static=False):
    """
    ball
    """
    if static:
        body_type = pymunk.Body.STATIC
    else:
        body_type = pymunk.Body.DYNAMIC
    body = pymunk.Body(body_type=body_type)
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.color = (255, 0, 0, 100)
    shape.elasticity = 0.8
    shape.mass = mass
    space.add(body, shape)
    return shape


def create_wall(space, pos, size, mass, static=True):
    """
    makes a wall
    :param space:
    :param pos:
    :param size:
    :param mass:
    :param static:
    """
    if static:
        body_type = pymunk.Body.STATIC
    else:
        body_type = pymunk.Body.DYNAMIC
    body = pymunk.Body(body_type=body_type)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size=size)
    shape.color = (0, 0, 0, 100)
    shape.elasticity = 0.2
    shape.mass = mass
    space.add(body, shape)
    return shape


def main():
    """
    main function
    """
    global delta_time
    pygame.init()
    camera_size = 800, 600
    window = pygame.display.set_mode(camera_size)

    space = pymunk.Space()
    space.gravity = (0, 10)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    clock = pygame.time.Clock()
    fps = 60
    mouse_start_pos = None
    balls = []
    line:  Optional[tuple] = None
    create_wall(space, (5, 400), (10, 800), 100)
    create_wall(space, (500, 595), (1000, 10), 100)
    while True:
        window.fill("#71ddee")

        if line is not None:
            pygame.draw.line(window, (255, 0, 0), *line, 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    balls.append(create_ball(space, event.pos, 20, 30, True))
                    mouse_start_pos = Vector2(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if mouse_start_pos is not None:
                    line = (mouse_start_pos, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    balls[-1].body.body_type = pymunk.Body.DYNAMIC
                    vec = (Vector2(event.pos) - mouse_start_pos)
                    vec *= 10
                    balls[-1].body.apply_impulse_at_local_point(tuple(vec), (0, 0))
                    mouse_start_pos = None
                    line = None

        space.debug_draw(draw_options)
        pygame.display.update()

        delta_time = clock.tick(fps) / 100
        space.step(delta_time)


if __name__ == "__main__":
    main()
