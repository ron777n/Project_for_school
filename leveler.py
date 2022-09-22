"""
This makes a level with images and the level data
"""
from functools import reduce

import pygame
from pygame.math import Vector2
from typing import List, Union
import json
import os


class Line(pygame.sprite.Sprite):
    """
    basic line so we could check collisions
    start_pos, end_pos, color=(255, 0, 0), width=10
    """

    def __init__(self, start_pos, end_pos, color=(255, 0, 0), width=10):
        super().__init__()
        self.start_pos: Vector2 = start_pos
        self.end_pos: Vector2 = end_pos
        self.color = color
        self.width = width
        self.rect = pygame.Rect(start_pos, (end_pos - start_pos) + Vector2(5, 5))
        self.horizontal = self.start_pos.y == self.end_pos.y
        self.vertical = self.start_pos.x == self.end_pos.x


class Level:
    """
    the level, has image shape, game details and hatboxes for the floors and walls
    """

    def __init__(self, window: Union[str, tuple, pygame.Surface]):
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

    def add_line(self, line: Line, draw=False):
        """
        adds a line to the the level
        :param line: the line to add
        :param draw: whether to draw the line or not
        """
        if draw:
            pygame.draw.rect(self.image, (255, 0, 0), line.rect)
        self.lines.add(line)


def build_levels(draw=False) -> list[Level]:
    """
    downloads all the levels and adds them to a list of levels
    :return: the list of levels
    """
    levels: List[Level] = []
    with open("levels_data.json") as levels_data:
        data = json.load(levels_data)
    level_images = os.listdir("level_images")

    for image, level_lines in zip(level_images, data.values()):
        level1 = Level(f"level_images/{image}")
        for x1, y1, x2, y2 in level_lines:
            line = Line(Vector2(min(x1, x2), min(y1, y2)), Vector2(max(x1, x2), max(y1, y2)))
            level1.add_line(line, draw)
        levels.append(level1)
    return levels


def join_levels(levels: list[Level]) -> Level:
    """
    takes a list of levels and returns it as one level
    """
    level_size = max(levels, key=lambda x: x.image.get_width()).image.get_width(), reduce(lambda a, b: a + b.image.get_height(), levels, 0)
    print(level_size)
    new_level: Level = Level(level_size)
    for i, level in enumerate(levels, 1):
        line: Line
        l_shape = level.shape
        new_level.image.blit(level.image, (0, level_size[1]-i*level.image.get_height()))
        for line in level.lines:
            new_line_start = line.start_pos + Vector2(0, level_size[1] - i* l_shape[1])
            new_line_end = line.end_pos + Vector2(0, level_size[1] - i * l_shape[1])
            new_level.add_line(Line(new_line_start, new_line_end, line.color, line.width))

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
