"""
Sisyphus' python template.
EGG
"""
import pygame

from .basics import Particle, particle_image


class RainParticle(Particle):
    """
    a rain drop particle
    """
    color = (60, 170, 255, 100)
    image = pygame.transform.scale(particle_image, (1, 10))

    def __init__(self, pos):
        super().__init__(pos, (0, 30), 4000)


RainParticle.set_color()


def main():
    """
    main function
    """


if __name__ == "__main__":
    main()
