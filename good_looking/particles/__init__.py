"""
fuck particles
"""
from typing import Union, Optional

import pygame
from pygame.math import Vector2
import random

from Utils.timing import Timer, dt, tick
from camera import CameraGroup


particle_image = pygame.image.load("sprites\\objects\\particle.png")


class ParticleEmitter(pygame.sprite.Sprite):
    """
    spawns particles
    """
    def __init__(self, particle_type, pos, timer: Optional[Timer] = None, offset=(False, 0, 0)):
        super().__init__()
        self.particle_type = particle_type
        self.timer = timer
        self.pos = pos
        self.offset = offset

    def update(self):
        if self.timer is None or not self.timer.check():
            if self.offset[0]:
                pos_x = self.pos[0] + random.uniform(-self.offset[1], self.offset[1])
                pos_y = self.pos[1] + random.uniform(-self.offset[2], self.offset[2])
                pos = pos_x, pos_y
            else:
                pos = self.pos
            particle = self.particle_type(pos)
            particles.add(particle)
            camera_group.add(particle)
            if self.timer is not None:
                self.timer.reset()


class Particle(pygame.sprite.Sprite):
    """
    fuck particle
    """
    color = (255, 0, 0, 255)
    image = particle_image.copy()

    def __init__(self, pos):
        super().__init__()
        self.pos = Vector2()
        x, y = random.uniform(-5, 5), -5
        self.direction = Vector2(x, y)
        self.rect = pygame.rect.Rect(*pos, 11, 11)
        self.death = Timer(500)

    @classmethod
    def set_color(cls):
        cls.image.fill(cls.color, None, pygame.BLEND_RGBA_MULT)
        cls.image.fill(cls.color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    def update(self):
        if not self.death.check():
            self.kill()
            return
        self.rect.centerx += self.direction[0] * dt[0]
        self.rect.centery += self.direction[1] * dt[0]


particles = pygame.sprite.Group()

camera_group = CameraGroup(pygame.Surface((600, 600)), (600, 600))


def main():
    """
    tests the camera
    """

    pygame.init()

    cam_shape = 600, 600
    Particle.set_color()
    screen = pygame.display.set_mode(cam_shape)
    particle_emitter = ParticleEmitter(Particle, (300, 300), Timer(25), (True, 40, 00))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    camera_group.zoom *= 1.5
                elif event.key in (pygame.K_MINUS, pygame.K_PLUS):
                    camera_group.zoom /= 1.5
            elif event.type == pygame.MOUSEMOTION:
                particle_emitter.pos = event.pos

        screen.fill("#71ddee")

        particle_emitter.update()

        particles.update()
        camera_group.update()
        camera_group.draw()

        pygame.display.update()
        tick(60)


if __name__ == '__main__':
    main()
