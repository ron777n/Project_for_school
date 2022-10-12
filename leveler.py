"""
This makes a level with images and the level data
"""
from functools import reduce

import pygame
import pymunk
from pygame.math import Vector2
from typing import List, Union, Sequence
import json
import os

import physics


class Line(physics.objects.Solid):
    """
    basic line so we could check collisions
    vertices[0], vertices[1], color=(255, 0, 0), width=10
    """

    def __init__(self, vertices: Sequence, color=(255, 0, 0), width=10):
        super().__init__(body_type=pymunk.Body.STATIC)
        if len(vertices) == 2:
            self.vertices = [(vertices[0][0] - width / 2, vertices[0][1] - width / 2),
                             (vertices[0][0] + width / 2, vertices[0][1] + width / 2),
                             (vertices[1][0] - width / 2, vertices[1][1] - width / 2),
                             (vertices[1][0] + width / 2, vertices[1][1] + width / 2), ]
        else:
            self.vertices = vertices
        self.shape = pymunk.Poly(self, self.vertices)
        self.shape.elasticity = 0.2
        self.shape.friction = 0.95
        self.shape.elasticity = 0.5
        self.color = color
        self.width = width
        self.size = (vertices[1][0] - vertices[0][0], vertices[1][1] - vertices[0][1])
        self.rect = pygame.Rect(vertices[0], Vector2(self.size) + Vector2(5, 5))


class Level(pymunk.Space):
    """
    the level, has image shape, game details and hatboxes for the floors and walls
    """

    def __init__(self, window: Union[str, tuple, pygame.Surface]):
        super().__init__()
        self.image: pygame.Surface
        if isinstance(window, str):
            self.image: pygame.image = pygame.image.load(window)
        elif isinstance(window, tuple):
            self.image: pygame.image = pygame.surface.Surface(window)
        elif isinstance(window, pygame.Surface):
            self.image = window
        else:
            raise ValueError("Bro what the fuck you doing?!?")
        self.lines = pygame.sprite.Group()
        self.levelNo = 0
        self.is_blizzard_level = False
        self.isIceLevel = False
        self.coins = []
        self.has_progression_coins = False
        self.shape = self.image.get_width(), self.image.get_height()
        self.gravity = (0, 10)

    def add_line(self, line: Line, draw=False):
        """
        adds a line to the the level
        :param line: the line to add
        :param draw: whether to draw the line or not
        """
        if draw:
            pygame.draw.rect(self.image, (255, 0, 0), line.rect)
        self.add(line, line.shape)
        self.lines.add(line)


def build_levels(draw=False) -> list[Level]:
    """
    downloads all the levels and adds them to a list of levels
    :return: the list of levels
    """
    levels: List[Level] = []
    with open("levels_data.json") as levels_data:
        data = json.load(levels_data)
    level_images = sorted(os.listdir("level_images"), key=lambda x: int(x[:-4]))

    for image, level_lines in zip(level_images, data.values()):
        level1 = Level(f"level_images/{image}")
        for x1, y1, x2, y2 in level_lines:
            line = Line(((x1, y1), (x2, y2)))
            level1.add_line(line, draw)
        levels.append(level1)
    return levels


def join_levels(levels: list[Level]) -> Level:
    """
    takes a list of levels and returns it as one level
    """
    level_size = max(levels, key=lambda x: x.image.get_width()).image.get_width(), reduce(
        lambda a, b: a + b.image.get_height(), levels, 0)
    new_level: Level = Level(level_size)
    for i, level in enumerate(levels, 1):
        line: Line
        l_shape = level.shape
        new_level.image.blit(level.image, (0, level_size[1] - i * level.image.get_height()))
        for line in level.lines:
            new_vertices = [(vertex[0], vertex[1] + level_size[1] - i * l_shape[1]) for vertex in line.vertices]
            new_level.add_line(Line(new_vertices, line.color, line.width))

    return new_level


def main():
    """
    main function
    """
    levels = build_levels()
    i = 0
    new_window = levels[i].image
    screen = pygame.display.set_mode((new_window.get_width(), new_window.get_height()))
    fps_clock = pygame.time.Clock()
    while True:
        screen.blit(new_window, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                i += 1
                i %= len(levels)
                new_window = levels[i].image
        pygame.display.flip()
        fps_clock.tick(60)


def level_test():
    """
    tests the join levels
    """
    levels = build_levels()
    level = join_levels(levels)
    new_window = level.image
    screen = pygame.display.set_mode((new_window.get_width(), new_window.get_height()), pygame.SCALED)
    fps_clock = pygame.time.Clock()
    while True:
        screen.blit(new_window, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        pygame.display.flip()
        fps_clock.tick(60)


if __name__ == "__main__":
    level_test()
