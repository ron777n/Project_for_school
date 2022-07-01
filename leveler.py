"""
This makes a level with images and the level data
"""

import pygame
from pygame.math import Vector2
from typing import List
import json
import os


class Line(pygame.sprite.Sprite):
    """
    basic line so we could check collisions
    start_pos, end_pos, color=(255, 0, 0), width=10
    """
    def __init__(self, start_pos, end_pos, color=(255, 0, 0), width=10):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.width = width
        self.rect = pygame.Rect(start_pos, (end_pos-start_pos)+Vector2(10, 10))
        self.horizontal = self.start_pos.y == self.end_pos.y
        self.vertical = self.start_pos.x == self.end_pos.x


class Level:
    """
    the level, has image shape, game details and hatboxes for the floors and walls
    """
    def __init__(self, window: str, draw=True):
        self.image: pygame.image = pygame.image.load(window)
        self.lines = pygame.sprite.Group()
        self.levelNo = 0
        self.is_blizzard_level = False
        self.isIceLevel = False
        self.coins = []
        self.has_progression_coins = False
        self.shape = self.image.get_width(), self.image.get_height()
        if draw:
            line: Line
            for line in self.lines:
                pygame.draw.rect(self.image, line.color, line.rect)

    def add_line(self, x1, y1, x2, y2):
        """
        adds a line to the the level
        :param x1: starting x pos
        :param y1: starting y pos
        :param x2: ending x pos
        :param y2: ending y pos
        """
        self.lines.add(Line(Vector2(min(x1, x2), min(y1, y2)), Vector2(max(x1, x2), max(y1, y2))))


def build_levels():
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
        for line in level_lines:
            level1.add_line(*line)
        levels.append(level1)
    return levels


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


if __name__ == "__main__":
    main()
