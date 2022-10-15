"""
if you want to have an object that can move
"""
import pygame
import pymunk

from physics.objects import Block, Solid


class LineWay(Block):
    """
    enables a body to move in only a single line
    """
    def __init__(self, space: pymunk.Space, rect):
        Solid.__init__(self, body_type=pymunk.Body.DYNAMIC)
        self.shape = pymunk.Poly.create_box(self, size=rect.size)
        self.create_shape(self.shape, rect)
        self._image = pygame.transform.scale(self._image, rect.size)
        self.image = self._image.copy()
        self.position = rect.center
        self.rect = rect
        joint = pymunk.GrooveJoint(space.static_body, self, (300, 200), (850, 200), (0, 0))
        space.add(self, self.shape, joint)
        self.velocity_func = self.velocity_function

    @staticmethod
    def velocity_function(body: 'Solid', gravity, damping, delta_time):
        pymunk.Body.update_velocity(body, (0, 0), damping, delta_time)
        body.angle = 0


def main():
    """
    main function
    """


if __name__ == "__main__":
    main()
