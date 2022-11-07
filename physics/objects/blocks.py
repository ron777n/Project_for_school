"""
for shit that you could place down
"""
from typing import Optional

import pygame
import pymunk
from pygame.math import Vector2

from Utils.Pygame import image_utils
from Utils.timing import Timer
from .basics import Solid, BaseObject


class Block(Solid):
    """
    simple Block bro
    """
    elasticity = 0.6
    strength = 1.0
    hardness = 1.0
    friction = 0.8
    density = 0.3
    _image = pygame.image.load('sprites/objects/block.png')
    emission: Optional[tuple] = None
    reflectivity: Optional[float] = None
    temperature: float = 10.0
    melting_point: float = 30.0
    opacity: float = 1.0

    def __init__(self, space, rect, *, body_type=pymunk.Body.DYNAMIC, **kwargs):
        super().__init__(body_type=body_type)
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect)
        self.shape = pymunk.Poly.create_box(self, size=rect.size)
        for kwarg, value in kwargs.items():
            setattr(self.shape, kwarg, value)
        self.create_shape(self.shape, rect)
        self.position = rect.center
        self.rect = rect
        self.size = rect.size
        space.add(self, self.shape)


class Turret(Solid):
    """
    simple object that can shoot lasers and look at a point
    """
    body_image = pygame.image.load("sprites/objects/turret_body.png")
    head_image = pygame.image.load("sprites/objects/turret_head.png")

    def __init__(self, _space, rect):
        super().__init__(body_type=pymunk.Body.KINEMATIC)
        self.position = rect.center
        self.shape = pymunk.Poly.create_box(self, size=rect.size)
        self.shape = self.create_shape(self.shape)
        self.direction: int = 0
        self.rect = rect
        self.turned = False

    def turn_to(self, point: pygame.Vector2):
        """
        points the object towards a point
        """
        diff_points = point - Vector2(self.rect.center)
        angle = diff_points.angle_to(Vector2())
        self.direction = angle

    @property
    def image(self) -> pygame.Surface:

        if abs(self.direction) > 90:
            head_image = pygame.transform.flip(self.head_image, False, True)
        else:  # abs(self.direction) < 90:
            head_image = pygame.transform.flip(self.head_image, False, False)
        head = pygame.transform.rotate(head_image, self.direction)
        head_rect = head.get_rect()
        body_rect = self.body_image.get_rect()
        body_rect.top = head_rect.centery + 15
        img = pygame.surface.Surface((max(body_rect.size[0], head_rect.size[0]),
                                      body_rect.size[1] + head_rect.size[1]),
                                     pygame.SRCALPHA)
        img.blit(head, (0, 0))
        img.blit(self.body_image, body_rect)
        return img


class Laser(BaseObject):
    """
    object with no mass, that isn't effected by any forces only by original velocity
    """
    _image: Optional[pygame.Surface] = pygame.transform.scale(pygame.image.load("sprites/objects/Laser.png"), (50, 10))

    emission: Optional[tuple] = (255, 0, 0)
    reflectivity: Optional[float]
    temperature: float = 1000.0
    melting_point: float = 0.0
    opacity: float = 0.5
    elasticity = 1
    mass = 1.01

    def __init__(self, space, start_point: Vector2, direction: Vector2, speed: int = 100):
        super().__init__()
        self.start_point = start_point
        self.speed = speed
        self.rect = pygame.Rect(50, 50, 10, 10)
        self.look_angle = direction.angle_to(Vector2())
        self.position = start_point
        direction.scale_to_length(speed)
        self.velocity = tuple(direction)
        self.shape = pymunk.Poly.create_box(self, (1, 1))
        self.shape = self.create_shape(self.shape)
        self.shape.elasticity = self.elasticity
        space.add(self, self.shape)
        self.velocity_func = self.velocity_fun
        self.death = Timer(4000)

    @property
    def image_angle(self):
        return -self.velocity.angle_degrees

    def update(self):
        if not self.death.check():
            self.kill()
            self.space.remove(self.shape, self)
            return

    @staticmethod
    def velocity_fun(body: 'Laser', _gravity, damping, delta_time):
        pymunk.Body.update_velocity(body, (0, 0), damping, delta_time)
        body.angle = 0
        body.velocity = body.velocity.scale_to_length(body.speed)


class SlipperyBlock(Block):
    """
    block that is also slippery
    """
    _image = image_utils.tint_image(Block._image, (0, 0, 255), 200)

    def __init__(self, space, rect, *, body_type=pymunk.Body.DYNAMIC, friction=0.5):
        super().__init__(space, rect, body_type=body_type, friction=friction)
        # self._image.fill((0, 0, 255, 127), self.rect)
