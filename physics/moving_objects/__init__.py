"""
if you want to have an object that can move
"""
import pygame
import pymunk

from physics.objects import Solid


class LineWay:
    """
    enables a body to move in only a single line
    """
    def __init__(self, body: pymunk.Body, rect: pygame.Rect, free_angle=True, speed=None, gravity=False):
        space = body.space
        shape = list(body.shapes)[0]
        joint = pymunk.GrooveJoint(space.static_body, body, rect.topleft, rect.bottomright, (0, 0))
        body.velocity_func, body.position_func = self.velocity_function(free_angle, speed, gravity)
        space.remove(body, shape)
        space.add(body, shape, joint)

    @staticmethod
    def velocity_function(free_angle, speed, grav):
        """
        yes
        :return:
        """
        def vel(body: 'Solid', gravity, damping, delta_time):
            """
            this calculates the velocity of the object each time pymunk asks to do it
            """
            if not grav:
                gravity = (0, 0)
            pymunk.Body.update_velocity(body, gravity, damping, delta_time)
            if speed is not None and body.velocity.length:
                body.velocity = body.velocity.scale_to_length(speed)

        def pos(body: 'Solid', dt):
            """
            this calculates the position of the body
            """
            pymunk.Body.update_position(body, dt)
            if not free_angle:
                body.angle = 0

        return vel, pos


def main():
    """
    main function
    """


if __name__ == "__main__":
    main()
