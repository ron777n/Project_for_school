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
    MAX_JUMPS = 2
    ACCELERATION = 0.3
    FRICTION = -0.10
    RUN_SPEED = 5
    TERMINAL_VELOCITY = 20
    GRAVITY = 0.6

    def __init__(self, level, start_x=340, start_y=240, sprite_path="sprites/player_sprites"):
        super().__init__()
        images = ('/run1.png', '/run2.png', '/run3.png', '/idle.png',
                  '/fall.png', '/fallen.png', '/jump.png', '/oof.png')
        self.images = [pygame.image.load(sprite_path + image_name) for image_name in images]

        self.blocks = level.lines
        self._level = level
        self.get_run_frame = cycle_generator(2)
        self.is_grounded = False
        self.bumped = False
        self.turn = False

        # Position and direction
        self.pos = Vector2((start_x, start_y))
        self.rect = self.images[0].get_rect(midbottom=self.pos)
        self.vel = Vector2(0, 0)
        self.jumps = self.MAX_JUMPS
        self._moving = 0

    @property
    def moving(self):
        """
        gets the direction, for the setter
        """
        return self._moving

    @moving.setter
    def moving(self, value):
        if not value:
            self._moving = value
            if self.is_grounded:
                self.land()
        else:
            self._moving = value

    @property
    def level(self):
        """
        gets level, made this for the setter
        :return:
        """
        return self.level

    @level.setter
    def level(self, new_level: leveler.Level):
        """
        sets the level and updates the blocks
        :param new_level: the new level
        """
        self.blocks = new_level.lines
        self._level = new_level

    def is_player_grounded(self):
        """
        checks if the player is above ground
        :return: whether or not he is grounded
        """
        rect_ = self.rect.copy()
        rect_.y += 1
        for line in self.blocks:
            if line.horizontal and rect_.colliderect(line.rect):
                return True
        return False

    def move(self):
        """
        moves the player however the values allows
        :return:
        """
        if self.is_grounded:
            if not self.is_player_grounded():
                self.is_grounded = False
                return
            if self.moving == -1:
                self.vel = Vector2(-RUN_SPEED, 0)
            elif self.moving == 1:
                self.vel = Vector2(RUN_SPEED, 0)
            else:
                self.vel = Vector2(0, 0)

        self.rect.midbottom = self.pos

    def check_collisions(self):
        """
        check collisions with the level shit
        :return:
        """
        hits = pygame.sprite.spritecollide(self, self.blocks, False)
        if not hits:
            return
        chosen_hit: leveler.Line = self.select_hit(hits)
        if not chosen_hit:
            return
        if chosen_hit.horizontal:
            if self.vel.y > 0:
                self.rect.bottom = chosen_hit.rect.top
                self.vel = Vector2(0, 0)
                if not self.is_grounded:
                    self.land()
            else:
                self.vel.y = 0 - self.vel.y / 2
                self.rect.top = chosen_hit.end_pos[1] + 10  # TODO add bump sound effect

        elif chosen_hit.vertical:
            if not self.is_grounded:
                self.vel.x = 0 - self.vel.x / 2
                self.bumped = True  # TODO add bump sound effect
            if not self.turn:
                self.rect.right = chosen_hit.rect.left
            else:
                self.rect.left = chosen_hit.rect.right
            if len(hits) > 1:
                if self.is_player_grounded():
                    self.land()
        self.pos = self.rect.midbottom

    def select_hit(self, hits):
        """
        selects a hit so that the check collisions wont have to do it on every one
        :param hits: the hit boxes
        :return: the hit that is important
        """
        if len(hits) == 1:
            return hits[0]

        if self.vel.y > 0:
            return min(hits, key=lambda x: min(abs(self.rect.top - x.rect.bottom),
                                               abs(self.rect.bottom - x.rect.top)) if x.horizontal else 1000)
        return min(hits, key=lambda x: min(abs(self.rect.top - x.rect.bottom),
                                           abs(self.rect.bottom - x.rect.top)) if x.horizontal else min(
            abs(self.rect.left - x.rect.centerx), abs(self.rect.right - x.rect.centerx)))

    def land(self):
        """
        sets everything for landing
        """
        self.is_grounded = True
        self.vel = Vector2(0, 0)
        self.bumped = False
        self.jumps = self.MAX_JUMPS

    def gravity_check(self):
        """
        sets the movement of y if player is not on ground
        """
        if not self.is_grounded:
            self.vel.y = min(self.vel.y + GRAVITY, TERMINAL_VELOCITY)

    def update(self):
        """
        runs everything
        """
        self.pos = Vector2(self.rect.midbottom)
        self.pos += self.vel
        self.gravity_check()
        self.rect.midbottom = self.pos
        self.check_collisions()
        if self.moving:
            self.move()

    @property
    def image(self):
        """
        gets the image by the parameters
        :return: the image
        """
        if self.moving and self.is_grounded:
            img_index = next(self.get_run_frame)
        elif self.bumped:
            img_index = 7
        elif not self.is_grounded:
            if self.vel.y > 0:
                img_index = 4
            else:
                img_index = 6
        else:
            img_index = 3

        if self.vel.x < 0:
            self.turn = True
        elif self.vel.x > 0:
            self.turn = False

        image_ = self.images[img_index].copy()

        if self.turn:
            image_ = pygame.transform.flip(image_, True, False)
        return image_

    def jump(self):
        """
        jumps
        :return:
        """
        if not self.jumps:
            return
        # self.is_falling = False
        self.is_grounded = False
        self.vel.y = -15
        self.jumps -= 1
