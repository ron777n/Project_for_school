"""
Sisyphus' python template.
EGG
"""
import pygame

from Utils.timing import Timer, dt
from typing import Optional
from pygame.math import Vector2
import random


class ParticleEmitter(pygame.sprite.Sprite):
    """
    spawns particle_type inside the center of the rect if rand=False else spawns it randomly inside the rect
    timer to set a cool down on the particles spawning, if None spawns particles every time it is updated
    multiplier is how many particles it spawns every update
    """
    def __init__(self, particle_type, rect, timer: Optional[Timer] = None, camera_group=None, rand=False, multiplier=1):
        super().__init__()
        self.particle_type = particle_type
        self.timer = timer
        self.rect = rect
        self.rand = rand
        self.camera_group = camera_group
        self.enabled = True
        self.multiplier = multiplier

    def update(self):
        """
        spawns particles
        :return:
        """
        if not self.enabled:
            return
        if self.timer is None or not self.timer.check():
            if self.rand:
                pos_x = self.rect.left + random.uniform(0, self.rect.width)
                pos_y = self.rect.top + random.uniform(0, self.rect.height)
                pos = pos_x, pos_y
            else:
                pos = self.rect.center
            for i in range(self.multiplier):
                particle = self.particle_type(pos)
                self.camera_group.add(particle)
            if self.timer is not None:
                self.timer.reset()


particle_image = pygame.image.load("sprites\\objects\\particle.png")


class Particle(pygame.sprite.Sprite):
    """
    fuck particle
    """
    color = (255, 0, 0, 255)
    image = particle_image.copy()

    def __init__(self, pos, direction=(random.uniform(-5, 5), -5), death_time=500):
        super().__init__()
        self.pos = Vector2()
        self.direction = Vector2(direction)
        self.rect = pygame.rect.Rect(*pos, 11, 11)
        self.pos = Vector2(self.rect.center)  # needed precision
        self.death = Timer(death_time)

    @classmethod
    def set_color(cls):
        """
        used to set the image for its class, didn't want to put this in the __init__ because i thought
        it'd be unnecessary computation when you only need to do this once when you create it.
        """
        cls.image.fill(cls.color, None, pygame.BLEND_RGBA_MULT)
        cls.image.fill(cls.color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    def update(self):
        """
        moves the particle, or kills it if its time is up
        :return:
        """
        if not self.death.check():
            self.kill()
            return
        self.pos.x += self.direction[0] * dt[0]
        self.pos.y += self.direction[1] * dt[0]
        self.rect.center = self.pos
