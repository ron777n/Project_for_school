"""
This makes a level with images and the level data
"""

import pygame
from pygame.math import Vector2
from typing import List
import json
import os


class Line(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos, color=(255, 0, 0), width=10):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.width = width
        self.rect = pygame.Rect(start_pos, (end_pos-start_pos)+Vector2(10, 10))

    def add_line(self, surface):
        # pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, self.width)
        pygame.draw.rect(surface, self.color, self.rect, 0)

    @property
    def horizontal(self):
        return self.start_pos.y == self.end_pos.y

    @property
    def vertical(self):
        return self.start_pos.x == self.end_pos.x

    def __str__(self):
        return f"Line: ( {self.start_pos}, {self.end_pos} )"


class Level:
    def __init__(self, window: str):
        self.window: pygame.image = pygame.image.load(window)

        self.lines = pygame.sprite.Group()
        # self.lines: List[Line] = []
        self.levelNo = 0
        self.is_blizzard_level = False
        self.isIceLevel = False
        self.coins = []
        self.has_progression_coins = False

    def add_line(self, x1, y1, x2, y2):
        self.lines.add(Line(Vector2(min(x1, x2), min(y1, y2)), Vector2(max(x1, x2), max(y1, y2))))

    def get_image(self):
        for line in self.lines:
            line.add_line(self.window)
        return self.window

    def get_line_group(self):
        return self.lines

    @property
    def shape(self):
        return self.window.get_width(), self.window.get_height()


def build_levels():
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
    new_window = levels[i].get_image()
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
                new_window = levels[i].get_image()
        pygame.display.flip()
        fps_clock.tick(60)


if __name__ == "__main__":
    main()
