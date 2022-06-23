"""
everything player
"""

import pygame
from pygame.math import Vector2
import leveler


ACCELERATION = 0.3
FRICTION = -0.10
RUN_SPEED = 5
TERMINAL_VELOCITY = 20
GRAVITY = 0.6


def cycle_generator(max_size):
    """
    calling next on this will cycle up and down the numbers from 0 to max_size
    :param max_size: the max size wanted, not inclusive
    """
    i = 0
    down = 1
    while 1:
        i += down
        if i == max_size or i == 0:
            down *= -1
        yield i


class Player(pygame.sprite.Sprite):
    """
    Spawn a player
    """

    def __init__(self, level):
        super().__init__()
        self.images = [pygame.image.load("sprites/run1.png"), pygame.image.load("sprites/run2.png"),
                       pygame.image.load("sprites/run3.png"), pygame.image.load("sprites/idle.png"),
                       pygame.image.load("sprites/fall.png"), pygame.image.load("sprites/fallen.png"),
                       pygame.image.load("sprites/jump.png"), pygame.image.load("sprites/oof.png"),
                       pygame.image.load("sprites/squat.png")]

        self.blocks = level.get_line_group()
        self._level = level
        self.rect = self.images[0].get_rect()
        self.current_image = 3
        self.get_run_frame = cycle_generator(2)
        self.is_grounded = False
        self.bumped = False
        self.running = False
        self.turn = False

        # Position and direction
        self.vx = 0
        self.pos = Vector2((340, 240))
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pre_vel = Vector2(0, 0)
        self.jumping = False

    @property
    def level(self):
        return self.level

    @level.setter
    def level(self, new_level: leveler.Level):
        self.blocks = new_level.get_line_group()
        self._level = new_level

    def is_player_grounded(self):
        rect_ = self.rect.copy()
        rect_.y += 1
        for line in self.blocks:
            if line.horizontal and rect_.colliderect(line.rect):
                return True
        return False

    def move(self):
        self.running = False
        if self.is_grounded:
            if not self.is_player_grounded():
                self.is_grounded = False
                return
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
                self.running = True
                self.vel = Vector2(-RUN_SPEED, 0)
            elif pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
                self.running = True
                self.vel = Vector2(RUN_SPEED, 0)
            else:
                self.vel = Vector2(0, 0)

        self.rect.midbottom = self.pos

    def check_collisions(self, group: pygame.sprite.Group = None):
        if group is None:
            group = self.blocks
        hits = pygame.sprite.spritecollide(self, group, False)
        if not hits:
            return
        chosen_hit: leveler.Line = self.select_hit(hits)
        might_land = False
        if not chosen_hit:
            return
        if chosen_hit.horizontal:
            if self.vel.y > 0:
                self.pos.y = chosen_hit.start_pos[1]
                if len(hits) > 1:
                    might_land = True
                    self.vel = Vector2(0, 0)
                else:
                    self.land()
            else:
                self.vel.y = 0 - self.vel.y / 2
                self.pos.y = chosen_hit.start_pos[1]  # TODO add bump sound effect

        elif chosen_hit.vertical:
            if not self.turn:
                self.pos.x = chosen_hit.start_pos[0] - self.rect.width * 0.60
            else:
                self.pos.x = chosen_hit.end_pos[0] + self.rect.width * 0.63
            if not self.is_grounded:
                self.vel.x = 0 - self.vel.x / 2
                self.bumped = True  # TODO add bump sound effect
            if len(hits) > 1:
                if might_land and self.is_player_grounded():
                    self.land()

    def select_hit(self, hits):
        if len(hits) == 1:
            return hits[0]
        if len(hits) == 2:
            vert: leveler.Line
            vert, horiz, diag = [None] * 3
            if hits[0].vertical:
                vert = hits[0]
            if hits[0].horizontal:
                horiz = hits[0]
            # if hits[0].isDiagonal:
            #     diag = hits[0]
            if hits[1].vertical:
                vert = hits[1]
            if hits[1].horizontal:
                horiz = hits[1]
            # if hits[1].isDiagonal:
            #     diag = hits[1]
            if vert and horiz:
                if self.vel.y < 0:
                    if vert.rect.midright[1] > horiz.rect.midright[1]:
                        return vert
                    return horiz
                else:
                    if vert.rect.midright[1] < horiz.rect.midright[1]:
                        return vert
                    else:
                        return horiz
            if horiz and diag:
                if diag.midright[1] > horiz.midright[1]:
                    return horiz
        max_correction_allowed = -(self.vel.copy())

        min_correction = 10_000

        line_: leveler.Line = hits[0]

        line: leveler.Line
        for line in hits:
            directed_correction: Vector2 = Vector2(0, 0)
            correction = 10_000
            if line.horizontal:
                if self.vel.y > 0:
                    directed_correction.y = line.start_pos[1] - (self.pos.y + self.rect.height)
                    correction = abs(directed_correction.y - (line.start_pos[1] - self.rect.height))
                else:
                    directed_correction.y = line.start_pos[1] - self.pos.y
                    correction = abs(self.pos.y - line.start_pos[1])
            elif line.vertical:
                if self.vel.x > 0:
                    directed_correction.x = line.start_pos[0] - (self.pos.x + self.rect.width)
                    correction = abs(self.pos.x - (line.start_pos[0] - self.rect.width))
                else:
                    directed_correction.x = line.start_pos[0] - self.pos.x
                    correction = abs(self.pos.x - line.start_pos[0])
            else:
                print("This bitch diagonal")

            if int(directed_correction.x) in range(0, int(max_correction_allowed.x)) and int(
                    directed_correction.y) in range(0, int(max_correction_allowed.y)):
                if correction < min_correction:
                    min_correction = correction
                    line_ = line

        print(line_)
        return line_

    def land(self):
        self.is_grounded = True
        self.vel = Vector2(0, 0)
        self.bumped = False

    def gravity_check(self):
        if not self.is_grounded:
            self.vel.y = min(self.vel.y + GRAVITY, TERMINAL_VELOCITY)

    def update(self):
        self.gravity_check()
        self.move()
        self.pos += self.vel
        self.pre_vel = self.vel.copy()
        self.check_collisions()

    @property
    def image(self):
        if self.jumping:
            self.current_image = 6
        elif self.running:
            self.current_image = next(self.get_run_frame)
        elif self.bumped:
            self.current_image = 7
        elif not self.is_grounded:
            self.current_image = 4
        else:
            self.current_image = 3

        if self.vel.x < 0:
            self.turn = True
        elif self.vel.x > 0:
            self.turn = False

        image_ = self.images[self.current_image].copy()

        if self.turn:
            image_ = pygame.transform.flip(image_, True, False)
        return image_

    def jump(self):
        if not self.is_grounded:
            return
        # self.is_falling = False
        self.is_grounded = False
        self.vel.y = -15