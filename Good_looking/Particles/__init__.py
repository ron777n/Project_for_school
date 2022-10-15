"""
fuck particles
"""
import pygame

from camera import CameraGroup
from Utils.timing import tick, Timer
from . import falling
from .basics import Particle, ParticleEmitter


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
