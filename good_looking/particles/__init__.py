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
    def __init__(self, particle_type, rect, timer: Optional[Timer] = None, camera_group=None, rand=False, mult=1):
        super().__init__()
        self.particle_type = particle_type
        self.timer = timer
        self.rect = rect
        self.rand = rand
        self.camera_group = camera_group
        self.enabled = True
        self.multiplier = mult

    def update(self):
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
        self.pos = Vector2(self.rect.center)  # needed precision
        self.death = Timer(500)

    @classmethod
    def set_color(cls):
        cls.image.fill(cls.color, None, pygame.BLEND_RGBA_MULT)
        cls.image.fill(cls.color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    def update(self):
        if not self.death.check():
            self.kill()
            return
        self.pos.x += self.direction[0] * dt[0]
        self.pos.y += self.direction[1] * dt[0]
        self.rect.center = self.pos


Particle.set_color()


def main():
    """
    tests the camera
    """

    pygame.init()

    cam_shape = 600, 600
    screen = pygame.display.set_mode(cam_shape)
    camera_group = CameraGroup(screen, cam_shape)
    particle_emitter = ParticleEmitter(Particle, pygame.Rect(300, 300, 40, 40), Timer(25), camera_group, True)
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
                pos = CameraGroup.global_mouse
                particle_emitter.rect.center = pos
            elif event.type == pygame.MOUSEBUTTONUP:
                print(CameraGroup.global_mouse, event.pos)

        screen.fill("#71ddee")

        particle_emitter.update()

        camera_group.update()
        camera_group.draw()

        pygame.display.update()
        tick(60)


if __name__ == '__main__':
    main()
